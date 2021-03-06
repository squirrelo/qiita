# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import TestCase, main
from datetime import datetime

import pandas as pd

from qiita_core.qiita_settings import qiita_config
from qiita_core.util import qiita_test_checker

import qiita_db as qdb


@qiita_test_checker()
class MetaUtilTests(TestCase):
    def setUp(self):
        self.old_portal = qiita_config.portal

    def tearDown(self):
        qiita_config.portal = self.old_portal

    def _set_artifact_private(self):
        self.conn_handler.execute(
            "UPDATE qiita.artifact SET visibility_id=3")

    def _set_artifact_public(self):
        self.conn_handler.execute(
            "UPDATE qiita.artifact SET visibility_id=2")

    def _unshare_studies(self):
        self.conn_handler.execute("DELETE FROM qiita.study_users")

    def _unshare_analyses(self):
        self.conn_handler.execute("DELETE FROM qiita.analysis_users")

    def test_get_accessible_filepath_ids(self):
        self._set_artifact_private()

        # shared has access to all study files and analysis files

        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('shared@foo.bar'))
        self.assertItemsEqual(obs, {
            1, 2, 3, 4, 5, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21})

        # Now shared should not have access to the study files
        self._unshare_studies()
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('shared@foo.bar'))
        self.assertItemsEqual(obs, {16, 14, 15, 13})

        # Now shared should not have access to any files
        self._unshare_analyses()
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('shared@foo.bar'))
        self.assertEqual(obs, set())

        # Now shared has access to public study files
        self._set_artifact_public()
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('shared@foo.bar'))
        self.assertEqual(obs, {1, 2, 3, 4, 5, 9, 12, 17, 18, 19, 20, 21})

        # Test that it doesn't break: if the SampleTemplate hasn't been added
        exp = {1, 2, 3, 4, 5, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('test@foo.bar'))
        self.assertEqual(obs, exp)

        info = {
            "timeseries_type_id": 1,
            "metadata_complete": True,
            "mixs_compliant": True,
            "number_samples_collected": 4,
            "number_samples_promised": 4,
            "study_alias": "TestStudy",
            "study_description": "Description of a test study",
            "study_abstract": "No abstract right now...",
            "emp_person_id": 1,
            "principal_investigator_id": 1,
            "lab_person_id": 1
        }
        qdb.study.Study.create(
            qdb.user.User('test@foo.bar'), "Test study", [1], info)
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('test@foo.bar'))
        self.assertEqual(obs, exp)

        # test in case there is a prep template that failed
        self.conn_handler.execute(
            "INSERT INTO qiita.prep_template (data_type_id) VALUES (2)")
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('test@foo.bar'))
        self.assertEqual(obs, exp)

        # admin should have access to everything
        count = self.conn_handler.execute_fetchone("SELECT count(*) FROM "
                                                   "qiita.filepath")[0]
        exp = set(range(1, count + 1))
        obs = qdb.meta_util.get_accessible_filepath_ids(
            qdb.user.User('admin@foo.bar'))
        self.assertEqual(obs, exp)

    def test_get_lat_longs(self):
        exp = [
            [74.0894932572, 65.3283470202],
            [57.571893782, 32.5563076447],
            [13.089194595, 92.5274472082],
            [12.7065957714, 84.9722975792],
            [44.9725384282, 66.1920014699],
            [10.6655599093, 70.784770579],
            [29.1499460692, 82.1270418227],
            [35.2374368957, 68.5041623253],
            [53.5050692395, 31.6056761814],
            [60.1102854322, 74.7123248382],
            [4.59216095574, 63.5115213108],
            [68.0991287718, 34.8360987059],
            [84.0030227585, 66.8954849864],
            [3.21190859967, 26.8138925876],
            [82.8302905615, 86.3615778099],
            [12.6245524972, 96.0693176066],
            [85.4121476399, 15.6526750776],
            [23.1218032799, 42.838497795],
            [43.9614715197, 82.8516734159],
            [68.51099627, 2.35063674718],
            [0.291867635913, 68.5945325743],
            [40.8623799474, 6.66444220187],
            [95.2060749748, 27.3592668624],
            [78.3634273709, 74.423907894],
            [38.2627021402, 3.48274264219]]

        obs = qdb.meta_util.get_lat_longs()
        self.assertItemsEqual(obs, exp)

    def test_get_lat_longs_EMP_portal(self):
        info = {
            'timeseries_type_id': 1,
            'lab_person_id': None,
            'principal_investigator_id': 3,
            'metadata_complete': False,
            'mixs_compliant': True,
            'study_description': 'desc',
            'study_alias': 'alias',
            'study_abstract': 'abstract'}

        study = qdb.study.Study.create(
            qdb.user.User('test@foo.bar'), 'test_study_1', efo=[1], info=info)
        qdb.portal.Portal('EMP').add_studies([study.id])

        md = {
            'my.sample': {
                'physical_specimen_location': 'location1',
                'physical_specimen_remaining': True,
                'dna_extracted': True,
                'sample_type': 'type1',
                'collection_timestamp': datetime(2014, 5, 29, 12, 24, 51),
                'host_subject_id': 'NotIdentified',
                'Description': 'Test Sample 4',
                'str_column': 'Value for sample 4',
                'int_column': 4,
                'latitude': 42.42,
                'longitude': 41.41,
                'taxon_id': 9606,
                'scientific_name': 'homo sapiens'}
        }

        md_ext = pd.DataFrame.from_dict(md, orient='index')
        qdb.metadata_template.sample_template.SampleTemplate.create(
            md_ext, study)

        qiita_config.portal = 'EMP'

        obs = qdb.meta_util.get_lat_longs()
        exp = [[42.42, 41.41]]

        self.assertItemsEqual(obs, exp)


if __name__ == '__main__':
    main()
