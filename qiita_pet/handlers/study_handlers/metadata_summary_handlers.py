# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from __future__ import division

from tornado.web import authenticated, HTTPError

from qiita_ware.util import dataframe_from_template, stats_from_df
from qiita_db.study import Study
from qiita_db.metadata_template import SampleTemplate, PrepTemplate
from qiita_db.exceptions import QiitaDBUnknownIDError
from qiita_pet.handlers.base_handlers import BaseHandler


class MetadataSummaryHandler(BaseHandler):
    def _get_template(self, constructor, template_id):
        """Given the id and the template constructor, instantiates the template

        Parameters
        ----------
        constructor : {PrepTemplate or SampleTemplate}
            The template constructor
        template_id : str or int
            The template id

        Returns
        -------
        PrepTemplate or SampleTemplate instance
            The instantiated object

        Raises
        ------
        HTTPError
            If the template does not exists
        """
        try:
            template = constructor(int(template_id))
        except (QiitaDBUnknownIDError, ValueError):
            # By using __name__, it will either display 'SampleTemplate'
            # or 'PrepTemplate'
            raise HTTPError(500, "%s %s does not exist" %
                                 (constructor.__name__, template_id))

        return template

    @authenticated
    def get(self, arguments):
        study_id = int(self.get_argument('study_id'))

        # Get the arguments
        prep_template = self.get_argument('prep_template', None)
        sample_template = self.get_argument('sample_template', None)

        if prep_template and sample_template:
            raise HTTPError(500, "You should provide either a sample template "
                                 "or a prep template, but not both")
        elif prep_template:
            # The prep template has been provided
            template = self._get_template(PrepTemplate, prep_template)
            back_button_path = (
                "/study/description/%s?top_tab=raw_data_tab&sub_tab=%s"
                "&prep_tab=%s" % (study_id, template.raw_data, template.id))
        elif sample_template:
            # The sample template has been provided
            template = self._get_template(SampleTemplate, sample_template)
            back_button_path = (
                "/study/description/%s?top_tab=sample_template_tab"
                % study_id)
        else:
            # Neither a sample template or a prep template has been provided
            # Fail nicely
            raise HTTPError(500, "You should provide either a sample template "
                                 "or a prep template")

        study = Study(template.study_id)

        # check whether or not the user has access to the requested information
        if not study.has_access(self.current_user):
            raise HTTPError(403, "You do not have access to access this "
                                 "information.")

        df = dataframe_from_template(template)
        stats = stats_from_df(df)

        self.render('metadata_summary.html',
                    study_title=study.title, stats=stats,
                    back_button_path=back_button_path)


class MetadataEditHandler(BaseHandler):
    def get(self, study_id):
        samples = ["Sample %d" % x for x in range(400)]
        metacols = ["Meta %d" % x for x in range(200)]

        self.render("edit_metadata.html",
                    samples=samples, metacols=metacols)

    def post(self, study_id):
        pass
