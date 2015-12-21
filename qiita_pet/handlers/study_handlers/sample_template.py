from tornado.web import authenticated, HTTPError

from qiita_pet.handlers.base_handlers import BaseHandler
from qiita_pet.util import is_localhost
from qiita_pet.handlers.util import download_link_or_path
from qiita_db.util import get_files_from_uploads_folders
from qiita_pet.handlers.api_proxy import (
    sample_template_info, process_sample_template, update_sample_template,
    delete_sample_template, get_sample_template_filepaths,
    study_data_types_proxy)


class SampleTemplateAJAX(BaseHandler):
    @authenticated
    def get(self):
        """Send formatted summary page of sample template"""
        study_id = self.get_argument('study_id')
        files = [f for _, f in get_files_from_uploads_folders(study_id)
                 if f.endswith(('txt', 'tsv'))]
        data_types = sorted(study_data_types_proxy())
        is_local = is_localhost(self.request.headers['host'])
        # Get the most recent version for download and build the link
        download = get_sample_template_filepaths(study_id,
                                                 self.current_user.id)[-1]
        dl_path = download_link_or_path(
            is_local, download[0], download[1], "Download sample information")

        stats = sample_template_info(study_id, self.current_user.id)
        self.render('study_ajax/sample_summary.html', stats=stats['summary'],
                    num_samples=stats['num_samples'], dl_path=dl_path,
                    files=files, study_id=study_id, data_types=data_types)

    @authenticated
    def post(self):
        """Edit/delete/recreate sample template"""
        action = self.get_argument('action')
        study_id = self.get_argument('study_id')
        if action == 'create':
            filepath = self.get_argument('filepath')
            data_type = self.get_argument('data_type')
            result = process_sample_template(study_id, self.current_user.id,
                                             data_type, filepath)
        elif action == 'update':
            filepath = self.get_argument('filepath')
            result = update_sample_template(study_id, self.current_user.id,
                                            filepath)
        elif action == 'delete':
            result = delete_sample_template(study_id, self.current_user.id)
        else:
            raise HTTPError(400, 'Unknown sample template action: %s' % action)
        self.write(result)