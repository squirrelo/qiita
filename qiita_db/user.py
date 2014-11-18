r"""
User object (:mod:`qiita_db.user`)
==================================

.. currentmodule:: qiita_db.user

This modules provides the implementation of the User class. This is used for
handling creation, deletion, and login of users, as well as retrieval of all
studies and analyses that are owned by or shared with the user.

Classes
-------

.. autosummary::
   :toctree: generated/

   User

Examples
--------
TODO
"""
# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from __future__ import division
from re import match

from qiita_core.exceptions import (IncorrectEmailError, IncorrectPasswordError,
                                   IncompetentQiitaDeveloperError)
from .base import QiitaObject
from .sql_connection import SQLConnectionHandler
from .util import (create_rand_string, check_table_cols, hash_password)
from .exceptions import (QiitaDBColumnError, QiitaDBDuplicateError)


class User(QiitaObject):
    """
    User object to access to the Qiita user information

    Attributes
    ----------
    email
    level
    info
    private_studies
    shared_studies
    private_analyses
    shared_analyses

    Methods
    -------
    change_password
    generate_reset_code
    change_forgot_password
    iter
    """

    _table = "qiita_user"
    # The following columns are considered not part of the user info
    _non_info = {"email", "user_level_id", "password"}

    def _check_id(self, id_, conn_handler=None):
        r"""Check that the provided ID actually exists in the database

        Parameters
        ----------
        id_ : object
            The ID to test
        conn_handler : SQLConnectionHandler
            The connection handler object connected to the DB

        Notes
        -----
        This function overwrites the base function, as sql layout doesn't
        follow the same conventions done in the other classes.
        """
        self._check_subclass()

        conn_handler = (conn_handler if conn_handler is not None
                        else SQLConnectionHandler())
        return conn_handler.execute_fetchone(
            "SELECT EXISTS(SELECT * FROM qiita.qiita_user WHERE "
            "email = %s)", (id_, ))[0]

    @classmethod
    def iter(cls):
        """Iterates over all users, sorted by their email addresses

        Returns
        -------
        generator
            Yields a user ID (email) for each user in the database,
            in order of ascending ID
        """
        conn_handler = SQLConnectionHandler()
        sql = """select email from qiita.{}""".format(cls._table)

        for result in conn_handler.execute_fetchall(sql):
            yield result[0]

    @classmethod
    def login(cls, email, password):
        """Logs a user into the system

        Parameters
        ----------
        email : str
            The email of the user
        password: str
            The plaintext password of the user

        Returns
        -------
        User object
            Returns the User object corresponding to the login information
            if correct login information

        Raises
        ------
        IncorrectEmailError
            Email passed is not a valid email
        IncorrectPasswordError
            Password passed is not correct for user
        """
        # see if user exists
        if not cls.exists(email):
            raise IncorrectEmailError("Email not valid: %s" % email)

        if not validate_password(password):
            raise IncorrectPasswordError("Password not valid!")

        # pull password out of database
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT password, user_level_id FROM qiita.{0} WHERE "
               "email = %s".format(cls._table))
        info = conn_handler.execute_fetchone(sql, (email, ))

        # verify user email verification
        # MAGIC NUMBER 5 = unverified email
        if int(info[1]) == 5:
            return False

        # verify password
        dbpass = info[0]
        hashed = hash_password(password, dbpass)
        if hashed == dbpass:
            return cls(email)
        else:
            raise IncorrectPasswordError("Password not valid!")

    @classmethod
    def exists(cls, email):
        """Checks if a user exists on the database

        Parameters
        ----------
        email : str
            the email of the user
        """
        if not validate_email(email):
            raise IncorrectEmailError("Email string not valid: %s" % email)
        conn_handler = SQLConnectionHandler()

        return conn_handler.execute_fetchone(
            "SELECT EXISTS(SELECT * FROM qiita.{0} WHERE "
            "email = %s)".format(cls._table), (email, ))[0]

    @classmethod
    def create(cls, email, password, info=None):
        """Creates a new user on the database

        Parameters
        ----------
        email : str
            The email of the user - used for log in
        password :
            The plaintext password of the user
        info: dict
            Other information for the user keyed to table column name

        Raises
        ------
        IncorrectPasswordError
            Password string given is not proper format
        IncorrectEmailError
            Email string given is not a valid email
        QiitaDBDuplicateError
            User already exists
        """
        # validate email and password for new user
        if not validate_email(email):
            raise IncorrectEmailError("Bad email given: %s" % email)
        if not validate_password(password):
            raise IncorrectPasswordError("Bad password given!")

        # make sure user does not already exist
        if cls.exists(email):
            raise QiitaDBDuplicateError("User", "email: %s" % email)

        # make sure non-info columns aren't passed in info dict
        if info:
            if cls._non_info.intersection(info):
                raise QiitaDBColumnError("non info keys passed: %s" %
                                         cls._non_info.intersection(info))
        else:
            info = {}

        # create email verification code and hashed password to insert
        # add values to info
        info["email"] = email
        info["password"] = hash_password(password)
        info["user_verify_code"] = create_rand_string(20, punct=False)

        # make sure keys in info correspond to columns in table
        conn_handler = SQLConnectionHandler()
        check_table_cols(conn_handler, info, cls._table)

        # build info to insert making sure columns and data are in same order
        # for sql insertion
        columns = info.keys()
        values = [info[col] for col in columns]

        sql = ("INSERT INTO qiita.%s (%s) VALUES (%s)" %
               (cls._table, ','.join(columns), ','.join(['%s'] * len(values))))
        conn_handler.execute(sql, values)
        return cls(email)

    @classmethod
    def verify_code(cls, email, code, code_type):
        """Verify that a code and email match

        Parameters
        ----------
        email : str
            email address of the user
        code : str
            code to verify
        code_type : {'create', 'reset'}

        Returns
        -------
        bool

        Raises
        ------
        IncompentQiitaDeveloper
            code_type is not create or reset
        """
        if code_type == 'create':
            column = 'user_verify_code'
        elif code_type == 'reset':
            column = 'pass_reset_code'
        else:
            raise IncompetentQiitaDeveloperError("code_type must be 'create'"
                                                 " or 'reset' Uknown type "
                                                 "%s" % code_type)
        sql = ("SELECT {1} from qiita.{0} where email"
               " = %s".format(cls._table, column))
        conn_handler = SQLConnectionHandler()
        db_code = conn_handler.execute_fetchone(sql, (email,))[0]
        if db_code == code and code_type == "create":
            # verify the user
            level = conn_handler.execute_fetchone(
                "SELECT user_level_id FROM qiita.user_level WHERE "
                "name = %s", ("user", ))[0]
            sql = ("UPDATE qiita.{} SET user_level_id = %s WHERE "
                   "email = %s".format(cls._table))
            conn_handler.execute(sql, (level, email))
        return db_code == code

    # ---properties---
    @property
    def email(self):
        """The email of the user"""
        return self._id

    @property
    def level(self):
        """The level of privileges of the user"""
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT ul.name from qiita.user_level ul JOIN qiita.{0} u ON "
               "ul.user_level_id = u.user_level_id WHERE "
               "u.email = %s".format(self._table))
        return conn_handler.execute_fetchone(sql, (self._id, ))[0]

    @property
    def info(self):
        """Dict with any other information attached to the user"""
        conn_handler = SQLConnectionHandler()
        sql = "SELECT * from qiita.{0} WHERE email = %s".format(self._table)
        # Need direct typecast from psycopg2 dict to standard dict
        info = dict(conn_handler.execute_fetchone(sql, (self._id, )))
        # Remove non-info columns
        for col in self._non_info:
            info.pop(col)
        return info

    @info.setter
    def info(self, info):
        """Updates the information attached to the user

        Parameters
        ----------
        info : dict
        """
        # make sure non-info columns aren't passed in info dict
        if self._non_info.intersection(info):
            raise QiitaDBColumnError("non info keys passed!")

        # make sure keys in info correspond to columns in table
        conn_handler = SQLConnectionHandler()
        check_table_cols(conn_handler, info, self._table)

        # build sql command and data to update
        sql_insert = []
        data = []
        # items used for py3 compatability
        for key, val in info.items():
            sql_insert.append("{0} = %s".format(key))
            data.append(val)
        data.append(self._id)

        sql = ("UPDATE qiita.{0} SET {1} WHERE "
               "email = %s".format(self._table, ','.join(sql_insert)))
        conn_handler.execute(sql, data)

    @property
    def private_studies(self):
        """Returns a list of private study ids owned by the user"""
        sql = ("SELECT study_id FROM qiita.study WHERE "
               "email = %s".format(self._table))
        conn_handler = SQLConnectionHandler()
        study_ids = conn_handler.execute_fetchall(sql, (self._id, ))
        return [s[0] for s in study_ids]

    @property
    def shared_studies(self):
        """Returns a list of study ids shared with the user"""
        sql = ("SELECT study_id FROM qiita.study_users WHERE "
               "email = %s".format(self._table))
        conn_handler = SQLConnectionHandler()
        study_ids = conn_handler.execute_fetchall(sql, (self._id, ))
        return [s[0] for s in study_ids]

    @property
    def private_analyses(self):
        """Returns a list of private analysis ids owned by the user"""
        sql = ("Select analysis_id from qiita.analysis WHERE email = %s AND "
               "analysis_status_id <> 6")
        conn_handler = SQLConnectionHandler()
        analysis_ids = conn_handler.execute_fetchall(sql, (self._id, ))
        return [a[0] for a in analysis_ids]

    @property
    def shared_analyses(self):
        """Returns a list of analysis ids shared with the user"""
        sql = ("SELECT analysis_id FROM qiita.analysis_users WHERE "
               "email = %s".format(self._table))
        conn_handler = SQLConnectionHandler()
        analysis_ids = conn_handler.execute_fetchall(sql, (self._id, ))
        return [a[0] for a in analysis_ids]

    # ------- methods ---------
    def change_password(self, oldpass, newpass):
        """Changes the password from oldpass to newpass

        Parameters
        ----------
        oldpass : str
            User's old password
        newpass : str
            User's new password

        Returns
        -------
        bool
            password changed or not
        """
        conn_handler = SQLConnectionHandler()
        dbpass = conn_handler.execute_fetchone(
            "SELECT password FROM qiita.{0} WHERE email = %s".format(
                self._table), (self._id, ))[0]
        if dbpass == hash_password(oldpass, dbpass):
            self._change_pass(newpass, conn_handler=conn_handler)
            return True
        return False

    def generate_reset_code(self):
        """Generates a password reset code for user"""
        reset_code = create_rand_string(20, punct=False)
        sql = ("UPDATE qiita.{0} SET pass_reset_code = %s, "
               "pass_reset_timestamp = NOW() WHERE email = %s".format(
                   self._table))
        conn_handler = SQLConnectionHandler()
        conn_handler.execute(sql, (reset_code, self._id))

    def change_forgot_password(self, code, newpass):
        """Changes the password if the code is valid

        Parameters
        ----------
        code : str
            User's forgotten password ID code
        newpass : str
            User's new password

        Returns
        -------
        bool
            password changed or not
        """
        if self.verify_code(self._id, code, "reset"):
            self._change_pass(newpass)
            return True
        return False

    def _change_pass(self, newpass, conn_handler=None):
        sql = ("UPDATE qiita.{0} SET password=%s, pass_reset_code=NULL WHERE "
               "email = %s".format(self._table))
        conn_handler = conn_handler if conn_handler else SQLConnectionHandler()
        conn_handler.execute(sql, (hash_password(newpass), self._id))


def validate_email(email):
    """Validates an email

    Notes
    -----
    A valid email must be of the form "string AT string" where the first string
    must be not empty, and consists of [a-zA-Z0-9.+]. The AT is the '@' symbol.
    The second string must be not empty, consist of [a-zA-Z0-9.], and is
    required to have at least one '.'.

    Parameters
    ----------
    email: str
        email to validate

    Returns
    -------
    bool
        Whether or not the email is valid
    """
    valid_chars = "a-zA-Z0-9\.\+\-"
    pattern = r"[%s]+@[%s]+\.[%s]+" % (valid_chars, valid_chars, valid_chars)

    try:
        email.encode('ascii')
    except UnicodeError:
        return False

    return True if match(pattern, email) is not None else False


def validate_password(password):
    """Validates a password

    Notes
    -----
    The valid characters for a password are:

        * lowercase letters
        * uppercase letters
        * numbers
        * special characters (e.g., !@#$%^&*()-_=+`~[]{}|;:'",<.>/?) with the
            exception of a backslash
        * must be ASCII
        * no spaces
        * must be at least 8 characters

    Parameters
    ----------
    password: str
        Password to validate

    Returns
    -------
    bool
        Whether or not the password is valid

    References
    -----
    http://stackoverflow.com/q/196345
    """
    if len(password) < 8:
        return False

    if "\\" in password or " " in password:
        return False

    try:
        password.encode('ascii')
    except UnicodeError:
        return False

    return True
