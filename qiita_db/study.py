r"""
Study and StudyPerson objects (:mod:`qiita_db.study`)
=====================================================

.. currentmodule:: qiita_db.study

This module provides the implementation of the Study and StudyPerson classes.
The study class allows access to all basic information including name and
pmids associated with the study, as well as returning ids for the data,
sample template, owner, and shared users. It is the central hub for creating,
deleting, and accessing a study in the database.

Contacts are taken care of by the StudyPerson class. This holds the contact's
name, email, address, and phone of the various persons in a study, e.g. The PI
or lab contact.

Classes
-------

.. autosummary::
   :toctree: generated/

   Study
   StudyPerson

Examples
--------
Studies contain contact people (PIs, Lab members, and EBI contacts). These
people have names, emails, addresses, and phone numbers. The email and name are
the minimum required information.

>>> from qiita_db.study import StudyPerson # doctest: +SKIP
>>> person = StudyPerson.create('Some Dude', 'somedude@foo.bar',
...                             address='111 fake street',
...                             phone='111-121-1313') # doctest: +SKIP
>>> person.name # doctest: +SKIP
Some dude
>>> person.email # doctest: +SKIP
somedude@foobar
>>> person.address # doctest: +SKIP
111 fake street
>>> person.phone # doctest: +SKIP
111-121-1313

A study requres a minimum of information to be created. Note that the people
must be passed as StudyPerson objects and the owner as a User object.

>>> from qiita_db.study import Study # doctest: +SKIP
>>> from qiita_db.user import User # doctest: +SKIP
>>> info = {
...     "timeseries_type_id": 1,
...     "metadata_complete": True,
...     "mixs_compliant": True,
...     "number_samples_collected": 25,
...     "number_samples_promised": 28,
...     "portal_type_id": 3,
...     "study_alias": "TST",
...     "study_description": "Some description of the study goes here",
...     "study_abstract": "Some abstract goes here",
...     "emp_person_id": StudyPerson(2),
...     "principal_investigator_id": StudyPerson(3),
...     "lab_person_id": StudyPerson(1)} # doctest: +SKIP
>>> owner = User('owner@foo.bar') # doctest: +SKIP
>>> Study(owner, "New Study Title", 1, info) # doctest: +SKIP

You can also add a study to an investigation by passing the investigation
object while creating the study.

>>> from qiita_db.study import Study # doctest: +SKIP
>>> from qiita_db.user import User # doctest: +SKIP
>>> from qiita_db.study import Investigation # doctest: +SKIP
>>> info = {
...     "timeseries_type_id": 1,
...     "metadata_complete": True,
...     "mixs_compliant": True,
...     "number_samples_collected": 25,
...     "number_samples_promised": 28,
...     "portal_type_id": 3,
...     "study_alias": "TST",
...     "study_description": "Some description of the study goes here",
...     "study_abstract": "Some abstract goes here",
...     "emp_person_id": StudyPerson(2),
...     "principal_investigator_id": StudyPerson(3),
...     "lab_person_id": StudyPerson(1)} # doctest: +SKIP
>>> owner = User('owner@foo.bar') # doctest: +SKIP
>>> investigation = Investigation(1) # doctest: +SKIP
>>> Study(owner, "New Study Title", 1, info, investigation) # doctest: +SKIP
"""

# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from __future__ import division
from future.utils import viewitems
from copy import deepcopy

from qiita_core.exceptions import IncompetentQiitaDeveloperError
from .base import QiitaStatusObject, QiitaObject
from .exceptions import (QiitaDBStatusError, QiitaDBColumnError, QiitaDBError)
from .util import check_required_columns, check_table_cols, convert_to_id
from .sql_connection import SQLConnectionHandler


class Study(QiitaStatusObject):
    r"""Study object to access to the Qiita Study information

    Attributes
    ----------
    data_types
    efo
    info
    investigation
    name
    pmids
    shared_with
    sample_template
    status
    title
    owner

    Methods
    -------
    raw_data
    preprocessed_data
    processed_data
    add_pmid
    exists
    has_access
    share
    unshare

    Notes
    -----
    All setters raise QiitaDBStatusError if trying to change a public study.
    You should not be doing that.
    """
    _table = "study"
    # The following columns are considered not part of the study info
    _non_info = {"email", "study_status_id", "study_title"}

    def _lock_public(self, conn_handler):
        """Raises QiitaDBStatusError if study is public"""
        if self.check_status(("public", )):
            raise QiitaDBStatusError("Illegal operation on public study!")

    def _status_setter_checks(self, conn_handler):
        r"""Perform a check to make sure not setting status away from public
        """
        self._lock_public(conn_handler)

    @classmethod
    def get_public(cls):
        """Returns study id for all public Studies

        Returns
        -------
        list of Study objects
            All public studies in the database
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT study_id FROM qiita.{0} WHERE "
               "{0}_status_id = %s".format(cls._table))
        # MAGIC NUMBER 2: status id for a public study
        return [x[0] for x in conn_handler.execute_fetchall(sql, (2, ))]

    @classmethod
    def exists(cls, study_title):
        """Check if a study exists based on study_title, which is unique

        Parameters
        ----------
        study_title : str
            The title of the study to search for in the database

        Returns
        -------
        bool
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT exists(select study_id from qiita.{} WHERE "
               "study_title = %s)").format(cls._table)

        return conn_handler.execute_fetchone(sql, [study_title])[0]

    @classmethod
    def create(cls, owner, title, efo, info, investigation=None):
        """Creates a new study on the database

        Parameters
        ----------
        owner : User object
            the study's owner
        title : str
            Title of the study
        efo : list
            Experimental Factor Ontology id(s) for the study
        info : dict
            the information attached to the study. All "*_id" keys must pass
            the objects associated with them.
        investigation : Investigation object, optional
            If passed, the investigation to associate with. Defaults to None.

        Raises
        ------
        QiitaDBColumnError
            Non-db columns in info dictionary
            All required keys not passed
        IncompetentQiitaDeveloperError
            email, study_id, study_status_id, or study_title passed as a key
            empty efo list passed

        Notes
        -----
        All keys in info, except the efo, must be equal to columns in
        qiita.study table in the database.
        """
        # make sure not passing non-info columns in the info dict
        if cls._non_info.intersection(info):
            raise QiitaDBColumnError("non info keys passed: %s" %
                                     cls._non_info.intersection(info))

        # make sure efo info passed
        if not efo:
            raise IncompetentQiitaDeveloperError("Need EFO information!")

        # add default values to info
        insertdict = deepcopy(info)
        insertdict['email'] = owner.id
        insertdict['study_title'] = title
        if "reprocess" not in insertdict:
            insertdict['reprocess'] = False
        # default to sandboxed status
        insertdict['study_status_id'] = 4

        # No nuns allowed
        insertdict = {k: v for k, v in viewitems(insertdict) if v is not None}

        conn_handler = SQLConnectionHandler()
        # make sure dictionary only has keys for available columns in db
        check_table_cols(conn_handler, insertdict, cls._table)
        # make sure reqired columns in dictionary
        check_required_columns(conn_handler, insertdict, cls._table)

        # Insert study into database
        sql = ("INSERT INTO qiita.{0} ({1}) VALUES ({2}) RETURNING "
               "study_id".format(cls._table, ','.join(insertdict),
                                 ','.join(['%s'] * len(insertdict))))
        # make sure data in same order as sql column names, and ids are used
        data = []
        for col in insertdict:
            if isinstance(insertdict[col], QiitaObject):
                data.append(insertdict[col].id)
            else:
                data.append(insertdict[col])

        study_id = conn_handler.execute_fetchone(sql, data)[0]

        # insert efo information into database
        sql = ("INSERT INTO qiita.{0}_experimental_factor (study_id, "
               "efo_id) VALUES (%s, %s)".format(cls._table))
        conn_handler.executemany(sql, [(study_id, e) for e in efo])

        # add study to investigation if necessary
        if investigation:
            sql = ("INSERT INTO qiita.investigation_study (investigation_id, "
                   "study_id) VALUES (%s, %s)")
            conn_handler.execute(sql, (investigation.id, study_id))

        return cls(study_id)

# --- Attributes ---
    @property
    def title(self):
        """Returns the title of the study

        Returns
        -------
        str
            Title of study
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT study_title FROM qiita.{0} WHERE "
               "study_id = %s".format(self._table))
        return conn_handler.execute_fetchone(sql, (self._id, ))[0]

    @title.setter
    def title(self, title):
        """Sets the title of the study

        Parameters
        ----------
        title : str
            The new study title
        """
        conn_handler = SQLConnectionHandler()
        self._lock_public(conn_handler)
        sql = ("UPDATE qiita.{0} SET study_title = %s WHERE "
               "study_id = %s".format(self._table))
        return conn_handler.execute(sql, (title, self._id))

    @property
    def info(self):
        """Dict with all information attached to the study

        Returns
        -------
        dict
            info of study keyed to column names
        """
        conn_handler = SQLConnectionHandler()
        sql = "SELECT * FROM qiita.{0} WHERE study_id = %s".format(self._table)
        info = dict(conn_handler.execute_fetchone(sql, (self._id, )))
        # remove non-info items from info
        for item in self._non_info:
            info.pop(item)
        # This is an optional column, but should not be considered part of the
        # info
        info.pop('study_id')
        return info

    @info.setter
    def info(self, info):
        """Updates the information attached to the study

        Parameters
        ----------
        info : dict
            information to change/update for the study, keyed to column name

        Raises
        ------
        IncompetentQiitaDeveloperError
            Empty dict passed
        QiitaDBColumnError
            Unknown column names passed
        """
        if not info:
            raise IncompetentQiitaDeveloperError("Need entries in info dict!")

        if 'study_id' in info:
            raise QiitaDBColumnError("Cannot set study_id!")

        if self._non_info.intersection(info):
            raise QiitaDBColumnError("non info keys passed: %s" %
                                     self._non_info.intersection(info))

        conn_handler = SQLConnectionHandler()
        self._lock_public(conn_handler)

        # make sure dictionary only has keys for available columns in db
        check_table_cols(conn_handler, info, self._table)

        sql_vals = []
        data = []
        # build query with data values in correct order for SQL statement
        for key, val in viewitems(info):
            sql_vals.append("{0} = %s".format(key))
            if isinstance(val, QiitaObject):
                data.append(val.id)
            else:
                data.append(val)
        data.append(self._id)

        sql = ("UPDATE qiita.{0} SET {1} WHERE "
               "study_id = %s".format(self._table, ','.join(sql_vals)))
        conn_handler.execute(sql, data)

    @property
    def efo(self):
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT efo_id FROM qiita.{0}_experimental_factor WHERE "
               "study_id = %s".format(self._table))
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id, ))]

    @efo.setter
    def efo(self, efo_vals):
        """Sets the efo for the study

        Parameters
        ----------
        efo_vals : list
            Id(s) for the new efo values

        Raises
        ------
        IncompetentQiitaDeveloperError
            Empty efo list passed
        """
        if not efo_vals:
            raise IncompetentQiitaDeveloperError("Need EFO information!")
        conn_handler = SQLConnectionHandler()
        self._lock_public(conn_handler)
        # wipe out any EFOs currently attached to study
        sql = ("DELETE FROM qiita.{0}_experimental_factor WHERE "
               "study_id = %s".format(self._table))
        conn_handler.execute(sql, (self._id, ))
        # insert new EFO information into database
        sql = ("INSERT INTO qiita.{0}_experimental_factor (study_id, "
               "efo_id) VALUES (%s, %s)".format(self._table))
        conn_handler.executemany(sql, [(self._id, efo) for efo in efo_vals])

    @property
    def shared_with(self):
        """list of users the study is shared with

        Returns
        -------
        list of User ids
            Users the study is shared with
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT email FROM qiita.{0}_users WHERE "
               "study_id = %s".format(self._table))
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id,))]

    @property
    def pmids(self):
        """ Returns list of paper PMIDs from this study

        Returns
        -------
        list of str
            list of all the PMIDs
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT pmid FROM qiita.{0}_pmid WHERE "
               "study_id = %s".format(self._table))
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id, ))]

    @property
    def investigation(self):
        """ Returns Investigation this study is part of

        Returns
        -------
        Investigation id
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT investigation_id FROM qiita.investigation_study WHERE "
               "study_id = %s")
        inv = conn_handler.execute_fetchone(sql, (self._id, ))
        return inv[0] if inv is not None else inv

    @property
    def sample_template(self):
        """ Returns sample_template information id

        Returns
        -------
        SampleTemplate id
        """
        return self._id

    @property
    def data_types(self):
        """Returns list of the data types for this study

        Returns
        -------
        list of str
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT DISTINCT DT.data_type FROM qiita.study_raw_data SRD "
               "JOIN qiita.prep_template PT ON SRD.raw_data_id = "
               "PT.raw_data_id JOIN qiita.data_type DT ON PT.data_type_id = "
               "DT.data_type_id WHERE SRD.study_id = %s")
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id,))]

    @property
    def owner(self):
        """Gets the owner of the study

        Returns
        -------
        str
            The email (id) of the user that owns this study
        """
        conn_handler = SQLConnectionHandler()
        sql = """select email from qiita.{} where study_id = %s""".format(
            self._table)

        return conn_handler.execute_fetchone(sql, [self._id])[0]

    # --- methods ---
    def raw_data(self, data_type=None):
        """ Returns list of data ids for raw data info

        Parameters
        ----------
        data_type : str, optional
            If given, retrieve only raw_data for given datatype. Default None.

        Returns
        -------
        list of RawData ids
        """
        spec_data = ""
        if data_type:
            spec_data = " AND data_type_id = %d" % convert_to_id(data_type,
                                                                 "data_type")
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT raw_data_id FROM qiita.study_raw_data WHERE "
               "study_id = %s{0}".format(spec_data))
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id,))]

    def add_raw_data(self, raw_data):
        """ Adds raw_data to the current study

        Parameters
        ----------
        raw_data : list of RawData
            The RawData objects to be added to the study

        Raises
        ------
        QiitaDBError
            If the raw_data is already linked to the current study
        """
        conn_handler = SQLConnectionHandler()
        queue = "%d_add_raw_data" % self.id
        sql = ("SELECT EXISTS(SELECT * FROM qiita.study_raw_data WHERE "
               "study_id=%s AND raw_data_id=%s)")
        conn_handler.create_queue(queue)
        sql_args = [(self.id, rd.id) for rd in raw_data]
        conn_handler.add_to_queue(queue, sql, sql_args, many=True)
        linked = conn_handler.execute_queue(queue)

        if any(linked):
            raise QiitaDBError("Some of the passed raw datas have been already"
                               " linked to the study %s" % self.id)

        conn_handler.executemany(
            "INSERT INTO qiita.study_raw_data (study_id, raw_data_id) "
            "VALUES (%s, %s)", sql_args)

    def preprocessed_data(self, data_type=None):
        """ Returns list of data ids for preprocessed data info

        Parameters
        ----------
        data_type : str, optional
            If given, retrieve only raw_data for given datatype. Default None.

        Returns
        -------
        list of PreprocessedData ids
        """
        spec_data = ""
        if data_type:
            spec_data = " AND data_type_id = %d" % convert_to_id(data_type,
                                                                 "data_type")
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT preprocessed_data_id FROM qiita.study_preprocessed_data"
               " WHERE study_id = %s{0}".format(spec_data))
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id,))]

    def processed_data(self, data_type=None):
        """ Returns list of data ids for processed data info

        Parameters
        ----------
        data_type : str, optional
            If given, retrieve only for given datatype. Default None.

        Returns
        -------
        list of ProcessedData ids
        """
        spec_data = ""
        if data_type:
            spec_data = " AND p.data_type_id = %d" % convert_to_id(data_type,
                                                                   "data_type")
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT p.processed_data_id FROM qiita.processed_data p JOIN "
               "qiita.study_processed_data sp ON p.processed_data_id = "
               "sp.processed_data_id WHERE "
               "sp.study_id = %s{0}".format(spec_data))
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id,))]

    def add_pmid(self, pmid):
        """Adds PMID to study

        Parameters
        ----------
        pmid : str
            pmid to associate with study
        """
        conn_handler = SQLConnectionHandler()
        sql = ("INSERT INTO qiita.{0}_pmid (study_id, pmid) "
               "VALUES (%s, %s)".format(self._table))
        conn_handler.execute(sql, (self._id, pmid))

    def has_access(self, user, no_public=False):
        """Returns whether the given user has access to the study

        Parameters
        ----------
        user : User object
            User we are checking access for
        no_public: bool
            If we should ignore those studies shared with the user. Defaults
            to False

        Returns
        -------
        bool
            Whether user has access to study or not
        """
        # if admin or superuser, just return true
        if user.level in {'superuser', 'admin'}:
            return True

        if no_public:
            return self._id in user.private_studies + user.shared_studies
        else:
            return self._id in user.private_studies + user.shared_studies \
                + self.get_public()

    def share(self, user):
        """Share the study with another user

        Parameters
        ----------
        user: User object
            The user to share the study with
        """
        conn_handler = SQLConnectionHandler()
        self._lock_public(conn_handler)

        # Make sure the study is not already shared with the given user
        if user.id in self.shared_with:
            return
        # Do not allow the study to be shared with the owner
        if user.id == self.owner:
            return

        sql = ("INSERT INTO qiita.study_users (study_id, email) VALUES "
               "(%s, %s)")

        conn_handler.execute(sql, (self._id, user.id))

    def unshare(self, user):
        """Unshare the study with another user

        Parameters
        ----------
        user: User object
            The user to unshare the study with
        """
        conn_handler = SQLConnectionHandler()
        self._lock_public(conn_handler)

        sql = ("DELETE FROM qiita.study_users WHERE study_id = %s AND "
               "email = %s")

        conn_handler.execute(sql, (self._id, user.id))


class StudyPerson(QiitaObject):
    r"""Object handling information pertaining to people involved in a study

    Attributes
    ----------
    name : str
        name of the person
    email : str
        email of the person
    affiliation : str
        institution with which the person is affiliated
    address : str or None
        address of the person
    phone : str or None
        phone number of the person
    """
    _table = "study_person"

    @classmethod
    def iter(cls):
        """Iterate over all study people in the database

        Returns
        -------
        generator
            Yields a `StudyPerson` object for each person in the database,
            in order of ascending study_person_id
        """
        conn = SQLConnectionHandler()
        sql = "select study_person_id from qiita.{} order by study_person_id"
        results = conn.execute_fetchall(sql.format(cls._table))

        for result in results:
            ID = result[0]
            yield StudyPerson(ID)

    @classmethod
    def exists(cls, name, affiliation):
        """Checks if a person exists

        Parameters
        ----------
        name: str
            Name of the person
        affiliation : str
            institution with which the person is affiliated

        Returns
        -------
        bool
            True if person exists else false
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT exists(SELECT * FROM qiita.{0} WHERE "
               "name = %s AND affiliation = %s)".format(cls._table))
        return conn_handler.execute_fetchone(sql, (name, affiliation))[0]

    @classmethod
    def create(cls, name, email, affiliation, address=None, phone=None):
        """Create a StudyPerson object, checking if person already exists.

        Parameters
        ----------
        name : str
            name of person
        email : str
            email of person
        affiliation : str
            institution with which the person is affiliated
        address : str, optional
            address of person
        phone : str, optional
            phone number of person

        Returns
        -------
        New StudyPerson object

        """
        if cls.exists(name, affiliation):
            sql = ("SELECT study_person_id from qiita.{0} WHERE name = %s and"
                   " affiliation = %s".format(cls._table))
            conn_handler = SQLConnectionHandler()
            spid = conn_handler.execute_fetchone(sql, (name, affiliation))

        # Doesn't exist so insert new person
        else:
            sql = ("INSERT INTO qiita.{0} (name, email, affiliation, address, "
                   "phone) VALUES"
                   " (%s, %s, %s, %s, %s) RETURNING "
                   "study_person_id".format(cls._table))
            conn_handler = SQLConnectionHandler()
            spid = conn_handler.execute_fetchone(sql, (name, email,
                                                       affiliation, address,
                                                       phone))
        return cls(spid[0])

    # Properties
    @property
    def name(self):
        """Returns the name of the person

        Returns
        -------
        str
            Name of person
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT name FROM qiita.{0} WHERE "
               "study_person_id = %s".format(self._table))
        return conn_handler.execute_fetchone(sql, (self._id, ))[0]

    @property
    def email(self):
        """Returns the email of the person

        Returns
        -------
        str
            Email of person
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT email FROM qiita.{0} WHERE "
               "study_person_id = %s".format(self._table))
        return conn_handler.execute_fetchone(sql, (self._id, ))[0]

    @property
    def affiliation(self):
        """Returns the affiliation of the person

        Returns
        -------
        str
            Affiliation of person
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT affiliation FROM qiita.{0} WHERE "
               "study_person_id = %s".format(self._table))
        return conn_handler.execute_fetchone(sql, [self._id])[0]

    @property
    def address(self):
        """Returns the address of the person

        Returns
        -------
        str or None
            address or None if no address in database
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT address FROM qiita.{0} WHERE study_person_id ="
               " %s".format(self._table))
        return conn_handler.execute_fetchone(sql, (self._id, ))[0]

    @address.setter
    def address(self, value):
        """Set/update the address of the person

        Parameters
        ----------
        value : str
            New address for person
        """
        conn_handler = SQLConnectionHandler()
        sql = ("UPDATE qiita.{0} SET address = %s WHERE "
               "study_person_id = %s".format(self._table))
        conn_handler.execute(sql, (value, self._id))

    @property
    def phone(self):
        """Returns the phone number of the person

        Returns
        -------
         str or None
            phone or None if no address in database
        """
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT phone FROM qiita.{0} WHERE "
               "study_person_id = %s".format(self._table))
        return conn_handler.execute_fetchone(sql, (self._id, ))[0]

    @phone.setter
    def phone(self, value):
        """Set/update the phone number of the person

        Parameters
        ----------
        value : str
            New phone number for person
        """
        conn_handler = SQLConnectionHandler()
        sql = ("UPDATE qiita.{0} SET phone = %s WHERE "
               "study_person_id = %s".format(self._table))
        conn_handler.execute(sql, (value, self._id))
