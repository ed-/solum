# Copyright 2015 - Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import app
from solum.api.controllers.v1.datamodel import workflow
from solum.api.handlers import app_handler
from solum.api.handlers import workflow_handler as wf_handler
from solum.common import exception
from solum.common import request
from solum.common import yamlutils
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class WorkflowController(rest.RestController):
    """Manages operations on a single workflow."""

    def __init__(self, app_id, wf_id):
        super(WorkflowController, self).__init__(self)
        self.app_id = app_id
        self.wf_id = wf_id

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(workflow.Workflow)
    def get(self):
        """Return this workflow."""
        request.check_request_for_https()
        ahandler = app_handler.AppHandler(pecan.request.security_context)
        app_model = ahandler.get(self.app_id)
        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        wf_model = handler.get(self.wf_id)
        wf_model = workflow.Workflow.from_db_model(wf_model,
                                                   pecan.request.host_url)
        return wf_model


class WorkflowsController(rest.RestController):
    """Manages operations on all of an app's workflows."""

    def __init__(self, app_id):
        super(WorkflowsController, self).__init__(self)
        self.app_id = app_id

    @pecan.expose()
    def _lookup(self, wf_uuid, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return WorkflowController(self.app_id, wf_uuid), remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(workflow.Workflow, body=workflow.Workflow, status_code=200)
    def post(self, data):
        """Create a new workflow."""
        request.check_request_for_https()
        if not data:
            raise exception.BadRequest(reason='No data.')

        ahandler = app_handler.AppHandler(pecan.request.security_context)
        app_model = ahandler.get(self.app_id)

        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        all_wfs = [workflow.Workflow.from_db_model(obj, pecan.request.host_url)
                   for obj in handler.get_all(app_id=self.app_id)]

        data.app_id = app_model.id
        data.config = app_model.workflow_config
        data.source = app_model.source

        # TODO(datsun180b): Do this incrementing properly. This isn't any kind of safe at all.
        # There isn't even a uniqueness constraint the table, though there ought to be.
        data.wf_id = len(all_wfs) + 1

        wf_data = data.as_dict(workflow.Workflow)
        return workflow.Workflow.from_db_model(handler.create(wf_data), pecan.request.host_url)


    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose([workflow.Workflow])
    def get_all(self):
        """Return all of one app's workflows, based on the query provided."""
        request.check_request_for_https()
        ahandler = app_handler.AppHandler(pecan.request.security_context)
        app_model = ahandler.get(self.app_id)
        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        all_wfs = [workflow.Workflow.from_db_model(obj, pecan.request.host_url)
                   for obj in handler.get_all(app_id=self.app_id)]
        return all_wfs
