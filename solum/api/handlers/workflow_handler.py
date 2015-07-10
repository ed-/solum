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

import datetime
import uuid

from solum.api.handlers import handler
from solum import objects
from solum.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class WorkflowHandler(handler.Handler):
    """Fulfills a request on the workflow resource."""

    def get(self, id):
        """Return a workflow."""
        return objects.registry.Workflow.get_by_uuid(self.context, id)

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

        db_obj.app_id = data['app_id']
        db_obj.wf_id = data['wf_id']
        db_obj.source = data['source']
        db_obj.config = data['config']
        db_obj.actions = data['actions']

        now = datetime.datetime.utcnow()
        db_obj.created_at = now
        db_obj.updated_at = now
        db_obj.create(self.context)
        return db_obj

    def get_all_by_id(self, resource_uuid):
        return objects.registry.UserlogList.get_all_by_id(
            self.context, resource_uuid=resource_uuid)

    def get_all(self, app_id=None):
        """Return all of an app's workflows."""
        return objects.registry.WorkflowList.get_all(self.context, app_id=app_id)
