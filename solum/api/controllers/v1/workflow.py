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

import pecan
from pecan import rest
import wsmeext.pecan as wsme_pecan

from solum.api.controllers.v1.datamodel import workflow
from solum.api.handlers import workflow_handler as wf_handler
from solum.common import exception
from solum.common import request
from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class WorkflowController(rest.RestController):
    """Manages operations on a single workflow."""

    @exception.wrap_pecan_controller_exception
    @pecan.expose()
    def get(self, app_id, wf_id):
        """Return this workflow."""
        request.check_request_for_https()
        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        wf_model = handler.get(wf_id)
        wf_model = workflow.Workflow.from_db_model(wf_model,
                                                   pecan.request.host_url)
        return wf_model


class WorkflowsController(rest.RestController):
    """Manages operations on all of an app's workflows."""

    @pecan.expose()
    def _lookup(self, wf_uuid, *remainder):
        if remainder and not remainder[-1]:
            remainder = remainder[:-1]
        return WorkflowController(wf_uuid), remainder

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose(workflow.Workflow, status_code=200)
    def post(self):
        """Create a new workflow for an app."""
        request.check_request_for_https()
        wf_data = {}
        if pecan.request.body and len(pecan.request.body) > 0:
            try:
                wf_data = yaml.load(pecan.request.body)
            except yaml.parser.ParseError as pe:
                raise exception.BadRequest(reason=pe.problem)
        if not wf_data.get('actions'):
            raise exception.BadRequest(reason='No actions specified.')

        handler = wf_handler.WorkflowHandler(pecan.request.security_context)

        new_workflow = handler.create(wf_data)
        created_wf = workflow.Workflow.from_db_model(new_wf, pecan.request.host_url)
        return created_wf

    @exception.wrap_pecan_controller_exception
    @wsme_pecan.wsexpose([workflow.Workflow])
    def get_all(self):
        """Return all of one app's workflows, based on the query provided."""
        request.check_request_for_https()
        handler = wf_handler.WorkflowHandler(pecan.request.security_context)
        all_wfs = [workflow.Workflow.from_db_model(obj, pecan.request.host_url)
                   for obj in handler.get_all()]
        return all_wfs
