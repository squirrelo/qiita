from unittest import TestCase, main

from qiita_core.util import qiita_test_checker
from qiita_db.portal import (
    add_study_to_portal, remove_study_from_portal, get_studies_by_portal)
from qiita_db.study import Study


@qiita_test_checker()
class TestPortal(TestCase):
    def setUp(self):
        self.study = Study(1)

    def test_get_by_portal(self):
        obs = get_studies_by_portal('EMP')
        self.assertEqual(obs, {1})

        obs = get_studies_by_portal('QIITA')
        self.assertEqual(obs, set())

    def test_add_portal(self):
        add_study_to_portal(self.study, 'QIITA')
        obs = self.study._portals
        self.assertEqual(obs, ['EMP', 'QIITA'])

    def test_remove_portal(self):
        remove_study_from_portal(self.study, 'EMP')
        obs = self.study._portals
        self.assertEqual(obs, [])


if __name__ == '__main__':
    main()