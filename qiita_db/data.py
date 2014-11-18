r"""
Data objects (:mod: `qiita_db.data`)
====================================

..currentmodule:: qiita_db.data

This module provides functionality for inserting, querying and deleting
data stored in the database. There are three data classes available: `RawData`,
`PreprocessedData` and `ProcessedData`.

Classes
-------

..autosummary::
    :toctree: generated/

    BaseData
    RawData
    PreprocessedData
    ProcessedData

Examples
--------
Assume we have a raw data instance composed by two fastq files (the sequence
file 'seqs.fastq' and the barcodes file 'barcodes.fastq') that belongs to
study 1.

Inserting the raw data into the database:

>>> from qiita_db.data import RawData
>>> from qiita_db.study import Study
>>> study = Study(1) # doctest: +SKIP
>>> filepaths = [('seqs.fastq', 1), ('barcodes.fastq', 2)]
>>> rd = RawData.create(2, filepaths, study) # doctest: +SKIP
>>> print rd.id # doctest: +SKIP
2

Retrieve the filepaths associated with the raw data

>>> rd.get_filepaths() # doctest: +SKIP
[('seqs.fastq', 'raw_sequences'), ('barcodes.fastq', 'raw_barcodes')]

Assume we have preprocessed the previous raw data files using the parameters
under the first row in the 'preprocessed_sequence_illumina_params', and we
obtained to files: a fasta file 'seqs.fna' and a qual file 'seqs.qual'.

Inserting the preprocessed data into the database

>>> from qiita_db.data import PreprocessedData
>>> filepaths = [('seqs.fna', 4), ('seqs.qual', 5)]
>>> ppd = PreprocessedData.create(rd, "preprocessed_sequence_illumina_params",
...                               1, filepaths) # doctest: +SKIP
>>> print ppd.id # doctest: +SKIP
2

Assume we have processed the previous preprocessed data on June 2nd 2014 at 5pm
using uclust and the first set of parameters, and we obtained a BIOM table.

Inserting the processed data into the database:

>>> from qiita_db.data import ProcessedData
>>> from datetime import datetime
>>> filepaths = [('foo/table.biom', 6)]
>>> date = datetime(2014, 6, 2, 5, 0, 0)
>>> pd = ProcessedData(ppd, "processed_params_uclust", 1,
...                    filepaths, date) # doctest: +SKIP
>>> print pd.id # doctest: +SKIP
2
"""

# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from __future__ import division
from datetime import datetime
from os.path import join
from functools import partial

from qiita_core.exceptions import IncompetentQiitaDeveloperError
from .base import QiitaObject
from .logger import LogEntry
from .sql_connection import SQLConnectionHandler
from .exceptions import QiitaDBError
from .util import (exists_dynamic_table, insert_filepaths, convert_to_id,
                   convert_from_id, purge_filepaths, get_filepath_id,
                   get_mountpoint)


class BaseData(QiitaObject):
    r"""Base class for the raw, preprocessed and processed data objects.

    Methods
    -------
    get_filepaths

    See Also
    --------
    RawData
    PreprocessedData
    PreprocessedData
    """
    _filepath_table = "filepath"

    # These variables should be defined in the subclasses. They are useful in
    # order to avoid code replication and be able to generalize the functions
    # included in this BaseClass
    _data_filepath_table = None
    _data_filepath_column = None

    def _link_data_filepaths(self, fp_ids, conn_handler):
        r"""Links the data `data_id` with its filepaths `fp_ids` in the DB
        connected with `conn_handler`

        Parameters
        ----------
        fp_ids : list of ints
            The filepaths ids to connect the data
        conn_handler : SQLConnectionHandler
            The connection handler object connected to the DB

        Raises
        ------
        IncompetentQiitaDeveloperError
            If called directly from the BaseClass or one of the subclasses does
            not define the class attributes _data_filepath_table and
            _data_filepath_column
        """
        # Create the list of SQL values to add
        values = [(self.id, fp_id) for fp_id in fp_ids]
        # Add all rows at once
        conn_handler.executemany(
            "INSERT INTO qiita.{0} ({1}, filepath_id) "
            "VALUES (%s, %s)".format(self._data_filepath_table,
                                     self._data_filepath_column), values)

    def add_filepaths(self, filepaths, conn_handler=None):
        r"""Populates the DB tables for storing the filepaths and connects the
        `self` objects with these filepaths"""
        # Check that this function has been called from a subclass
        self._check_subclass()

        # Check if the connection handler has been provided. Create a new
        # one if not.
        conn_handler = conn_handler if conn_handler else SQLConnectionHandler()

        # Update the status of the current object
        self._set_link_filepaths_status("linking")

        try:
            # Add the filepaths to the database
            fp_ids = insert_filepaths(filepaths, self._id, self._table,
                                      self._filepath_table, conn_handler)

            # Connect the raw data with its filepaths
            self._link_data_filepaths(fp_ids, conn_handler)
        except Exception as e:
            # Something went wrong, update the status
            self._set_link_filepaths_status("failed: %s" % e)
            LogEntry.create('Runtime', str(e),
                            info={self.__class__.__name__: self.id})
            raise e

        # Filepaths successfully added, update the status
        self._set_link_filepaths_status("idle")

    def get_filepaths(self):
        r"""Returns the filepaths and filetypes associated with the data object

        Returns
        -------
        list of tuples
            A list of (path, filetype) with all the paths associated with
            the current data
        """
        self._check_subclass()
        # We need a connection handler to the database
        conn_handler = SQLConnectionHandler()
        # Retrieve all the (path, id) tuples related with the current data
        # object. We need to first check the _data_filepath_table to get the
        # filepath ids of the filepath associated with the current data object.
        # We then can query the filepath table to get those paths.
        db_paths = conn_handler.execute_fetchall(
            "SELECT filepath, filepath_type_id FROM qiita.{0} WHERE "
            "filepath_id IN (SELECT filepath_id FROM qiita.{1} WHERE "
            "{2}=%(id)s)".format(self._filepath_table,
                                 self._data_filepath_table,
                                 self._data_filepath_column), {'id': self.id})

        _, fb = get_mountpoint(self._table, conn_handler)[0]
        base_fp = partial(join, fb)

        return [(base_fp(fp), convert_from_id(fid, "filepath_type",
                conn_handler)) for fp, fid in db_paths]

    def get_filepath_ids(self):
        self._check_subclass()
        conn_handler = SQLConnectionHandler()
        db_ids = conn_handler.execute_fetchall(
            "SELECT filepath_id FROM qiita.{0} WHERE "
            "{1}=%(id)s".format(self._data_filepath_table,
                                self._data_filepath_column), {'id': self.id})
        return [fp_id[0] for fp_id in db_ids]

    @property
    def link_filepaths_status(self):
        self._check_subclass()
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT link_filepaths_status FROM qiita.{0} "
            "WHERE {1}=%s".format(self._table, self._data_filepath_column),
            (self._id,))[0]

    def _set_link_filepaths_status(self, status):
        """Updates the link_filepaths_status of the object

        Parameters
        ----------
        status : str
            The new status

        Raises
        ------
        ValueError
            If the status is unknown
        """
        self._check_subclass()
        if (status not in ('idle', 'linking', 'unlinking') and
                not status.startswith('failed')):
            msg = 'Unknown status: %s' % status
            LogEntry.create('Runtime', msg,
                            info={self.__class__.__name__: self.id})
            raise ValueError(msg)

        conn_handler = SQLConnectionHandler()
        conn_handler.execute(
            "UPDATE qiita.{0} SET link_filepaths_status = %s "
            "WHERE {1} = %s".format(self._table, self._data_filepath_column),
            (status, self._id))


class RawData(BaseData):
    r"""Object for dealing with raw data

    Attributes
    ----------
    studies
    investigation_type

    Methods
    -------
    create
    data_type
    preprocessed_data

    See Also
    --------
    BaseData
    """
    # Override the class variables defined in the base classes
    _table = "raw_data"
    _data_filepath_table = "raw_filepath"
    _data_filepath_column = "raw_data_id"
    # Define here the class name, so in case it changes in the database we
    # only need to change it here
    _study_raw_table = "study_raw_data"

    @classmethod
    def create(cls, filetype, studies, filepaths=None):
        r"""Creates a new object with a new id on the storage system

        Parameters
        ----------
        filetype : int
            The filetype identifier
        studies : list of Study
            The list of Study objects to which the raw data belongs to
        filepaths : iterable of tuples (str, int), optional
            The list of paths to the raw files and its filepath type identifier

        Returns
        -------
        A new instance of `cls` to access to the RawData stored in the DB
        """
        # Add the raw data to the database, and get the raw data id back
        conn_handler = SQLConnectionHandler()
        rd_id = conn_handler.execute_fetchone(
            "INSERT INTO qiita.{0} (filetype_id) VALUES (%s) "
            "RETURNING raw_data_id".format(cls._table), (filetype,))[0]

        # Instantiate the object with the new id
        rd = cls(rd_id)

        # Connect the raw data with its studies
        values = [(study.id, rd_id) for study in studies]
        conn_handler.executemany(
            "INSERT INTO qiita.{0} (study_id, raw_data_id) VALUES "
            "(%s, %s)".format(rd._study_raw_table), values)

        # If file paths have been provided, add them to the raw data object
        if filepaths:
            rd.add_filepaths(filepaths, conn_handler)

        return rd

    @property
    def studies(self):
        r"""The IDs of the studies to which this raw data belongs

        Returns
        -------
        list of int
            The list of study ids to which the raw data belongs to
        """
        conn_handler = SQLConnectionHandler()
        ids = conn_handler.execute_fetchall(
            "SELECT study_id FROM qiita.{0} WHERE "
            "raw_data_id=%s".format(self._study_raw_table),
            [self._id])
        return [id[0] for id in ids]

    @property
    def filetype(self):
        r"""Returns the raw data filetype

        Returns
        -------
        str
            The raw data's filetype
        """
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT f.type FROM qiita.filetype f JOIN qiita.{0} r ON "
            "f.filetype_id = r.filetype_id WHERE "
            "r.raw_data_id=%s".format(self._table),
            (self._id,))[0]

    def data_types(self, ret_id=False):
        """Returns the list of data_types or data_type_ids

        Parameters
        ----------
        ret_id : bool, optional
            Return the id instead of the string, default False

        Returns
        -------
        list of str or int
            string values of data_type or ints if data_type_id
        """
        ret = "_id" if ret_id else ""
        conn_handler = SQLConnectionHandler()
        data_types = conn_handler.execute_fetchall(
            "SELECT d.data_type{0} FROM qiita.data_type d JOIN "
            "qiita.prep_template p ON p.data_type_id = d.data_type_id "
            "WHERE p.raw_data_id = %s".format(ret), (self._id, ))
        return [dt[0] for dt in data_types]

    @property
    def prep_templates(self):
        conn_handler = SQLConnectionHandler()
        sql = ("SELECT prep_template_id FROM qiita.prep_template "
               "WHERE raw_data_id = %s")
        return [x[0] for x in conn_handler.execute_fetchall(sql, (self._id,))]

    def _is_preprocessed(self, conn_handler=None):
        """Returns whether the RawData has been preprocessed or not

        Parameters
        ----------
        conn_handler : SQLConnectionHandler
            The connection handler object connected to the DB

        Returns
        -------
        bool
            whether the RawData has been preprocessed or not
        """
        conn_handler = conn_handler if conn_handler else SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT EXISTS(SELECT * FROM qiita.prep_template_preprocessed_data"
            " PTPD JOIN qiita.prep_template PT ON PT.prep_template_id = "
            "PTPD.prep_template_id WHERE PT.raw_data_id = %s)", (self._id,))[0]

    def _remove_filepath(self, fp, conn_handler, queue):
        """Removes the filepath from the RawData

        Parameters
        ----------
        fp : str
            The filepath to remove
        conn_handler : SQLConnectionHandler
            The connection handler object connected to the DB
        queue : str
            The queue to use in the conn_handler

        Raises
        ------
        QiitaDBError
            If the RawData has been already preprocessed
        IncompetentQiitaDeveloperError
            If the queue is provided but not the conn_handler
        ValueError
            If fp does not belong to the raw data
        """
        # If the RawData has been already preprocessed, we cannot remove any
        # file - raise an error
        if self._is_preprocessed(conn_handler):
            msg = ("Cannot clear all the filepaths from raw data %s, it has "
                   "been already preprocessed" % self._id)
            self._set_link_filepaths_status("failed: %s" % msg)
            raise QiitaDBError(msg)

        # Get the filpeath id
        fp_id = get_filepath_id(self._table, fp, conn_handler)
        fp_is_mine = conn_handler.execute_fetchone(
            "SELECT EXISTS(SELECT * FROM qiita.{0} WHERE filepath_id=%s AND "
            "{1}=%s)".format(self._data_filepath_table,
                             self._data_filepath_column),
            (fp_id, self._id))[0]

        if not fp_is_mine:
            msg = ("The filepath %s does not belong to raw data %s"
                   % (fp, self._id))
            self._set_link_filepaths_status("failed: %s" % msg)
            raise ValueError(msg)

        # We can remove the file
        sql = "DELETE FROM qiita.{0} WHERE filepath_id=%s".format(
            self._data_filepath_table)
        sql_args = (fp_id,)
        conn_handler.add_to_queue(queue, sql, sql_args)

    def clear_filepaths(self):
        """Removes all the filepaths attached to the RawData

        Raises
        ------
        QiitaDBError
            If the RawData has been already preprocessed
        """
        conn_handler = SQLConnectionHandler()

        queue = "%s_clear_fps" % self.id
        conn_handler.create_queue(queue)

        self._set_link_filepaths_status("unlinking")

        for fp, fp_type in self.get_filepaths():
            self._remove_filepath(fp, conn_handler, queue)

        try:
            # Execute all the queue
            conn_handler.execute_queue(queue)
        except Exception as e:
            self._set_link_filepaths_status("failed: %s" % e)
            LogEntry.create('Runtime', str(e),
                            info={self.__class__.__name__: self.id})
            raise e

        # We can already update the status to done, as the files have been
        # unlinked, the purge_filepaths call will not change the status
        # of the raw data object
        self._set_link_filepaths_status("idle")

        # Delete the files, if they are not used anywhere
        purge_filepaths(conn_handler)

    def remove_filepath(self, fp):
        """Removes the filepath from the RawData

        Parameters
        ----------
        fp : str
            The filepath to remove
        """
        conn_handler = SQLConnectionHandler()
        queue = "remove_fp_%s" % self.id
        conn_handler.create_queue(queue)

        # Set the current status to unlinking
        self._set_link_filepaths_status("unlinking")

        self._remove_filepath(fp, conn_handler, queue)

        try:
            # Execute the queue
            conn_handler.execute_queue(queue)
        except Exception as e:
            self._set_link_filepaths_status("failed: %s" % e)
            LogEntry.create('Runtime', str(e),
                            info={self.__class__.__name__: self.id})
            raise e

        # We can already update the status to done, as the files have been
        # unlinked, the purge_filepaths call will not change the status
        # of the raw data object
        self._set_link_filepaths_status("idle")

        # Delete the file if it is not used anywhere
        purge_filepaths(conn_handler)


class PreprocessedData(BaseData):
    r"""Object for dealing with preprocessed data

    Attributes
    ----------
    raw_data
    study
    prep_template
    ebi_submission_accession
    ebi_study_accession
    files

    Methods
    -------
    create
    is_submitted_to_insdc
    data_type

    See Also
    --------
    BaseData
    """
    # Override the class variables defined in the base classes
    _table = "preprocessed_data"
    _data_filepath_table = "preprocessed_filepath"
    _data_filepath_column = "preprocessed_data_id"
    _study_preprocessed_table = "study_preprocessed_data"
    _template_preprocessed_table = "prep_template_preprocessed_data"

    @classmethod
    def create(cls, study, preprocessed_params_table, preprocessed_params_id,
               filepaths, prep_template=None, data_type=None,
               submitted_to_insdc_status='not submitted',
               ebi_submission_accession=None,
               ebi_study_accession=None):
        r"""Creates a new object with a new id on the storage system

        Parameters
        ----------
        study : Study
            The study to which this preprocessed data belongs to
        preprocessed_params_table : str
            Name of the table that holds the preprocessing parameters used
        preprocessed_params_id : int
            Identifier of the parameters from the `preprocessed_params_table`
            table used
        filepaths : iterable of tuples (str, int)
            The list of paths to the preprocessed files and its filepath type
            identifier
        submitted_to_insdc_status : str, {'not submitted', 'submitting', \
                'success', 'failed'} optional
            Submission status of the raw data files
        prep_template : PrepTemplate, optional
            The PrepTemplate object used to generate this preprocessed data
        data_type : str, optional
            The data_type of the preprocessed_data
        ebi_submission_accession : str, optional
            The ebi_submission_accession of the preprocessed_data
        ebi_study_accession : str, optional
            The ebi_study_accession of the preprocessed_data

        Raises
        ------
        IncompetentQiitaDeveloperError
            If the table `preprocessed_params_table` does not exists
        IncompetentQiitaDeveloperError
            If data_type does not match that of prep_template passed
        """
        conn_handler = SQLConnectionHandler()

        # Sanity checks for the preprocesses_data data_type
        if ((data_type and prep_template) and
                data_type != prep_template.data_type):
            raise IncompetentQiitaDeveloperError(
                "data_type passed does not match prep_template data_type!")
        elif data_type is None and prep_template is None:
            raise IncompetentQiitaDeveloperError("Neither data_type nor "
                                                 "prep_template passed!")
        elif prep_template:
            # prep_template passed but no data_type,
            # so set to prep_template data_type
            data_type = prep_template.data_type(ret_id=True)
        else:
            # only data_type, so need id from the text
            data_type = convert_to_id(data_type, "data_type", conn_handler)

        # Check that the preprocessed_params_table exists
        if not exists_dynamic_table(preprocessed_params_table, "preprocessed_",
                                    "_params", conn_handler):
            raise IncompetentQiitaDeveloperError(
                "Preprocessed params table '%s' does not exists!"
                % preprocessed_params_table)

        # Add the preprocessed data to the database,
        # and get the preprocessed data id back
        ppd_id = conn_handler.execute_fetchone(
            "INSERT INTO qiita.{0} (preprocessed_params_table, "
            "preprocessed_params_id, submitted_to_insdc_status, data_type_id, "
            "ebi_submission_accession, ebi_study_accession) VALUES "
            "(%(param_table)s, %(param_id)s, %(insdc)s, %(data_type)s, "
            "%(ebi_submission_accession)s, %(ebi_study_accession)s) "
            "RETURNING preprocessed_data_id".format(cls._table),
            {'param_table': preprocessed_params_table,
             'param_id': preprocessed_params_id,
             'insdc': submitted_to_insdc_status,
             'data_type': data_type,
             'ebi_submission_accession': ebi_submission_accession,
             'ebi_study_accession': ebi_study_accession})[0]
        ppd = cls(ppd_id)

        # Connect the preprocessed data with its study
        conn_handler.execute(
            "INSERT INTO qiita.{0} (study_id, preprocessed_data_id) "
            "VALUES (%s, %s)".format(ppd._study_preprocessed_table),
            (study.id, ppd.id))

        # If the prep template was provided, connect the preprocessed data
        # with the prep_template
        if prep_template is not None:
            conn_handler.execute(
                "INSERT INTO qiita.{0} (prep_template_id, "
                "preprocessed_data_id) VALUES "
                "(%s, %s)".format(cls._template_preprocessed_table),
                (prep_template.id, ppd_id))

        # Add the filepaths to the database and connect them
        ppd.add_filepaths(filepaths, conn_handler)
        return ppd

    @property
    def prep_template(self):
        r"""The prep template used to generate the preprocessed data"""
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT prep_template_id FROM qiita.{0} WHERE "
            "preprocessed_data_id=%s".format(
                self._template_preprocessed_table), (self._id,))[0]

    @property
    def study(self):
        r"""The ID of the study to which this preprocessed data belongs

        Returns
        -------
        int
            The study id to which this preprocessed data belongs to"""
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT study_id FROM qiita.{0} WHERE "
            "preprocessed_data_id=%s".format(self._study_preprocessed_table),
            [self._id])[0]

    @property
    def ebi_submission_accession(self):
        r"""The ebi submission accession of this preprocessed data

        Returns
        -------
        str
            The ebi submission accession of this preprocessed data
        """
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT ebi_submission_accession FROM qiita.{0} "
            "WHERE preprocessed_data_id=%s".format(self._table), (self.id,))[0]

    @property
    def ebi_study_accession(self):
        r"""The ebi study accession of this preprocessed data

        Returns
        -------
        str
            The ebi study accession of this preprocessed data
        """
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT ebi_study_accession FROM qiita.{0} "
            "WHERE preprocessed_data_id=%s".format(self._table), (self.id,))[0]

    @ebi_submission_accession.setter
    def ebi_submission_accession(self, new_ebi_submission_accession):
        """ Sets the ebi_submission_accession for the preprocessed_data

        Parameters
        ----------
        new_ebi_submission_accession: str
            The new ebi submission accession
        """
        conn_handler = SQLConnectionHandler()

        sql = ("UPDATE qiita.{0} SET ebi_submission_accession = %s WHERE "
               "preprocessed_data_id = %s").format(self._table)
        conn_handler.execute(sql, (new_ebi_submission_accession, self._id))

    @ebi_study_accession.setter
    def ebi_study_accession(self, new_ebi_study_accession):
        """ Sets the ebi_study_accession for the preprocessed_data

        Parameters
        ----------
        new_ebi_study_accession: str
            The new ebi study accession
        """
        conn_handler = SQLConnectionHandler()

        sql = ("UPDATE qiita.{0} SET ebi_study_accession = %s WHERE "
               "preprocessed_data_id = %s").format(self._table)
        conn_handler.execute(sql, (new_ebi_study_accession, self._id))

    def data_type(self, ret_id=False):
        """Returns the data_type or data_type_id

        Parameters
        ----------
        ret_id : bool, optional
            Return the id instead of the string, default False

        Returns
        -------
        str or int
            string value of data_type or data_type_id
        """
        conn_handler = SQLConnectionHandler()
        ret = "_id" if ret_id else ""
        data_type = conn_handler.execute_fetchone(
            "SELECT d.data_type{0} FROM qiita.data_type d JOIN "
            "qiita.{1} p ON p.data_type_id = d.data_type_id WHERE"
            " p.preprocessed_data_id = %s".format(ret, self._table),
            (self._id, ))
        return data_type[0]

    def submitted_to_insdc_status(self):
        r"""Tells if the raw data has been submitted to INSDC

        Returns
        -------
        str
            One of {'not submitted', 'submitting', 'success', 'failed'}
        """
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT submitted_to_insdc_status FROM qiita.{0} "
            "WHERE preprocessed_data_id=%s".format(self._table), (self.id,))[0]

    def update_insdc_status(self, state, study_acc=None, submission_acc=None):
        r"""Update the INSDC submission status

        Parameters
        ----------
        state : str, {'not submitted', 'submitting', 'success', 'failed'}
            The current status of submission
        study_acc : str, optional
            The study accession from EBI. This is not optional if ``state`` is
            ``success``.
        submission_acc : str, optional
            The submission accession from EBI. This is not optional if
            ``state`` is ``success``.

        Raises
        ------
        ValueError
            If the state is not known.
        ValueError
            If ``state`` is ``success`` and either ``study_acc`` or
            ``submission_acc`` are ``None``.
        """
        if state not in ('not submitted', 'submitting', 'success', 'failed'):
            raise ValueError("Unknown state: %s" % state)

        conn_handler = SQLConnectionHandler()

        if state == 'success':
            if study_acc is None or submission_acc is None:
                raise ValueError("study_acc or submission_acc is None!")

            conn_handler.execute("""
                UPDATE qiita.{0}
                SET (submitted_to_insdc_status,
                     ebi_study_accession,
                     ebi_submission_accession) = (%s, %s, %s)
                WHERE preprocessed_data_id=%s""".format(self._table),
                                 (state, study_acc, submission_acc, self.id))
        else:
            conn_handler.execute("""
                UPDATE qiita.{0}
                SET submitted_to_insdc_status = %s
                WHERE preprocessed_data_id=%s""".format(self._table),
                                 (state, self.id))


class ProcessedData(BaseData):
    r"""Object for dealing with processed data

    Attributes
    ----------
    preprocessed_data
    study

    Methods
    -------
    create
    data_type

    See Also
    --------
    BaseData
    """
    # Override the class variables defined in the base classes
    _table = "processed_data"
    _data_filepath_table = "processed_filepath"
    _data_filepath_column = "processed_data_id"
    _study_processed_table = "study_processed_data"
    _preprocessed_processed_table = "preprocessed_processed_data"

    @classmethod
    def create(cls, processed_params_table, processed_params_id, filepaths,
               preprocessed_data=None, study=None, processed_date=None,
               data_type=None):
        r"""
        Parameters
        ----------
        processed_params_table : str
            Name of the table that holds the preprocessing parameters used
        processed_params_id : int
            Identifier of the parameters from the `processed_params_table`
            table used
        filepaths : iterable of tuples (str, int)
            The list of paths to the processed files and its filepath type
            identifier
        preprocessed_data : PreprocessedData, optional
            The PreprocessedData object used as base to this processed data
        study : Study, optional
            If preprocessed_data is not provided, the study the processed data
            belongs to
        processed_date : datetime, optional
            Date in which the data have been processed. Default: now
        data_type : str, optional
            data_type of the processed_data. Otherwise taken from passed
            preprocessed_data.

        Raises
        ------
        IncompetentQiitaDeveloperError
            If the table `processed_params_table` does not exists
            If `preprocessed_data` and `study` are provided at the same time
            If `preprocessed_data` and `study` are not provided
        """
        conn_handler = SQLConnectionHandler()
        if preprocessed_data is not None:
            if study is not None:
                raise IncompetentQiitaDeveloperError(
                    "You should provide either preprocessed_data or study, "
                    "but not both")
            elif data_type is not None and \
                    data_type != preprocessed_data.data_type():
                raise IncompetentQiitaDeveloperError(
                    "data_type passed does not match preprocessed_data "
                    "data_type!")
            else:
                data_type = preprocessed_data.data_type(ret_id=True)
        else:
            if study is None:
                raise IncompetentQiitaDeveloperError(
                    "You should provide either a preprocessed_data or a study")
            if data_type is None:
                raise IncompetentQiitaDeveloperError(
                    "You must provide either a preprocessed_data, a "
                    "data_type, or both")
            else:
                data_type = convert_to_id(data_type, "data_type", conn_handler)

        # We first check that the processed_params_table exists
        if not exists_dynamic_table(processed_params_table,
                                    "processed_params_", "", conn_handler):
            raise IncompetentQiitaDeveloperError(
                "Processed params table %s does not exists!"
                % processed_params_table)

        # Check if we have received a date:
        if processed_date is None:
            processed_date = datetime.now()

        # Add the processed data to the database,
        # and get the processed data id back
        pd_id = conn_handler.execute_fetchone(
            "INSERT INTO qiita.{0} (processed_params_table, "
            "processed_params_id, processed_date, data_type_id) VALUES ("
            "%(param_table)s, %(param_id)s, %(date)s, %(data_type)s) RETURNING"
            " processed_data_id".format(cls._table),
            {'param_table': processed_params_table,
             'param_id': processed_params_id,
             'date': processed_date,
             'data_type': data_type})[0]

        pd = cls(pd_id)

        if preprocessed_data is not None:
            conn_handler.execute(
                "INSERT INTO qiita.{0} (preprocessed_data_id, "
                "processed_data_id) VALUES "
                "(%s, %s)".format(cls._preprocessed_processed_table),
                (preprocessed_data.id, pd_id))
            study_id = preprocessed_data.study
        else:
            study_id = study.id

        # Connect the processed data with the study
        conn_handler.execute(
            "INSERT INTO qiita.{0} (study_id, processed_data_id) VALUES "
            "(%s, %s)".format(cls._study_processed_table),
            (study_id, pd_id))

        pd.add_filepaths(filepaths, conn_handler)
        return cls(pd_id)

    @property
    def preprocessed_data(self):
        r"""The preprocessed data id used to generate the processed data"""
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT preprocessed_data_id FROM qiita.{0} WHERE "
            "processed_data_id=%s".format(self._preprocessed_processed_table),
            [self._id])[0]

    @property
    def study(self):
        r"""The ID of the study to which this processed data belongs

        Returns
        -------
        int
            The study id to which this processed data belongs"""
        conn_handler = SQLConnectionHandler()
        return conn_handler.execute_fetchone(
            "SELECT study_id FROM qiita.{0} WHERE "
            "processed_data_id=%s".format(self._study_processed_table),
            [self._id])[0]

    def data_type(self, ret_id=False):
        """Returns the data_type or data_type_id

        Parameters
        ----------
        ret_id : bool, optional
            Return the id instead of the string, default False

        Returns
        -------
        str or int
            string value of data_type or data_type_id
        """
        conn_handler = SQLConnectionHandler()
        ret = "_id" if ret_id else ""
        data_type = conn_handler.execute_fetchone(
            "SELECT d.data_type{0} FROM qiita.data_type d JOIN "
            "qiita.{1} p ON p.data_type_id = d.data_type_id WHERE"
            " p.processed_data_id = %s".format(ret, self._table),
            (self._id, ))
        return data_type[0]
