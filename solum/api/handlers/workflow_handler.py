# Copyright 2015 Rackspace Hosting
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

import uuid

from solum.api.handlers import handler
from solum import objects
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class WorkflowHandler(handler.Handler):
    """Fulfills a request on the workflow resource."""

    def get(self, id):
        """Return a workflow."""
        #return objects.registry.Workflow.get_by_uuid(self.context, id)
        return objects.registry.Workflow(wf_id=id)

    def delete(self, id):
        """Delete an existing workflow."""
        db_obj = objects.registry.Workflow.get_by_uuid(self.context, id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new workflow."""
        db_obj = objects.registry.Workflow()
        db_obj.id = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        db_obj.deleted = False

        # Fetch this data from the parent app.
        #db_obj.wf_id = max([0] + [wf.wf_id for wf in app.workflows]) + 1
        #db_obj.source = app.source
        #db_obj.config = app.workflow_config

        db_obj.actions = data.get('actions', [])

        db_obj.create(self.context)
        return db_obj

    def get_all(self, app_id=None):
        """Return all of an app's workflows."""
        #all_wfs = objects.registry.WorkflowList.get_all(self.context)
        #if app_id_id is not None:
        #    all_wfs = all_wfs.filter_by(app_id=app_id)
        #return all_wfs
        return []
