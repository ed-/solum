# Copyright (c) 2014 Rackspace Hosting
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

import base64
import errno
import os
import shelve
import uuid

from Crypto.PublicKey import RSA
from oslo.config import cfg

from solum.api.handlers import handler
from solum.common import clients
from solum import objects
from solum.openstack.common import log as logging
from solum.worker import api as worker_api

API_PARAMETER_OPTS = [
    cfg.StrOpt('system_param_store',
               default='database',
               help="Tells where to store system generated parameters, e.g. "
                    "deploy keys for cloning a private repo. "
                    "Options: database, barbican, local_file. "
                    "Defaults to database"),
    cfg.StrOpt('system_param_file',
               default='/etc/solum/secrets/git_secrets.db',
               help="The local file to store system generated parameters when "
                    "system_param_store is set to 'local_file'"),
]

CONF = cfg.CONF
CONF.register_opts(API_PARAMETER_OPTS, group='api')

LOG = logging.getLogger(__name__)

sys_param_store = CONF.api.system_param_store


class PlanHandler(handler.Handler):
    """Fulfills a request on the plan resource."""

    def get(self, id):
        """Return a plan."""
        return objects.registry.Plan.get_by_uuid(self.context, id)

    def update(self, id, data):
        """Modify existing plan."""
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        db_obj.raw_content.update(dict((k, v) for k, v in data.items()
                                       if k != 'parameters'))
        to_update = {'raw_content': db_obj.raw_content}
        if 'name' in data:
            to_update['name'] = data['name']

        updated = objects.registry.Plan.safe_update(self.context,
                                                    id, to_update)
        return updated

    def delete(self, id):
        """Delete existing plan."""
        db_obj = objects.registry.Plan.get_by_uuid(self.context, id)
        self._delete_params(db_obj.id)
        db_obj.destroy(self.context)

    def create(self, data):
        """Create a new plan."""
        db_obj = objects.registry.Plan()
        if 'name' in data:
            db_obj.name = data['name']
        db_obj.uuid = str(uuid.uuid4())
        db_obj.user_id = self.context.user
        db_obj.project_id = self.context.tenant
        sys_params = {}
        deploy_keys = []
        for artifact in data.get('artifacts', []):
            if (('content' not in artifact) or
                    ('private' not in artifact['content']) or
                    (not artifact['content']['private'])):
                continue
            new_key = RSA.generate(2048)
            public_key = new_key.publickey().exportKey("OpenSSH")
            private_key = new_key.exportKey("PEM")
            artifact['content']['public_key'] = public_key
            deploy_keys.append({'source_url': artifact['content']['href'],
                                'private_key': private_key})
        if deploy_keys:
            encoded_payload = base64.b64encode(bytes(str(deploy_keys)))
            repo_deploy_keys = ''
            if sys_param_store == 'database':
                repo_deploy_keys = encoded_payload
            elif sys_param_store == 'local_file':
                secrets_file = CONF.api.system_param_file
                try:
                    os.makedirs(os.path.dirname(secrets_file), 0o700)
                except OSError as ex:
                    if ex.errno != errno.EEXIST:
                        raise
                s = shelve.open(secrets_file)
                try:
                    s[db_obj.uuid] = encoded_payload
                    repo_deploy_keys = db_obj.uuid
                finally:
                    s.close()
            elif sys_param_store == 'barbican':
                client = clients.OpenStackClients(None).barbican().admin_client
                repo_deploy_keys = client.secrets.create(
                    name=db_obj.uuid,
                    payload=encoded_payload,
                    payload_content_type='application/octet-stream',
                    payload_content_encoding='base64').store()

            if repo_deploy_keys:
                sys_params['REPO_DEPLOY_KEYS'] = repo_deploy_keys
        db_obj.raw_content = dict((k, v) for k, v in data.items()
                                  if k != 'parameters')
        db_obj.create(self.context)

        user_params = data.get('parameters')
        self._create_params(db_obj.id, user_params, sys_params)
        return db_obj

    def get_all(self):
        """Return all plans."""
        return objects.registry.PlanList.get_all(self.context)

    def trigger_workflow(self, trigger_id, commit_sha='',
                         status_url=None, collab_url=None):
        """Get trigger by trigger id and start git workflow associated."""
        # Note: self.context will be None at this point as this is a
        # non-authenticated request.
        plan_obj = objects.registry.Plan.get_by_trigger_id(None, trigger_id)
        # get the trust context and authenticate it.
        try:
            self.context = self._context_from_trust_id(plan_obj.trust_id)
        except exception.AuthorizationFailure as auth_ex:
            LOG.warn(auth_ex)
            return

        artifacts = plan_obj.raw_content.get('artifacts', [])
        for arti in artifacts:
            if repo_utils.verify_artifact(arti, collab_url):
                self._build_artifact(plan_obj.id, artifact=arti,
                                     commit_sha=commit_sha,
                                     status_url=status_url)


    def _build_artifact(self, plan_id, artifact, verb='build', commit_sha='',
                        status_url=None):

        # This is a tempory hack so we don't need the build client
        # in the requirements.
        image = objects.registry.Image()
        image.name = artifact['name']
        image.source_uri = artifact['content']['href']
        image.base_image_id = artifact.get('language_pack', 'auto')
        image.source_format = artifact.get('artifact_type',
                                           CONF.api.source_format)
        image.image_format = CONF.api.image_format
        image.uuid = str(uuid.uuid4())
        image.user_id = self.context.user
        image.project_id = self.context.tenant
        image.state = IMAGE_STATES.PENDING
        image.create(self.context)
        test_cmd = artifact.get('unittest_cmd')
        repo_token = artifact.get('repo_token')

        git_info = {
            'source_url': image.source_uri,
            'commit_sha': commit_sha,
            'repo_token': repo_token,
            'status_url': status_url
        }

        if test_cmd:
            repo_utils.send_status(0, status_url, repo_token, pending=True)

        # assemblyHandler.get_all_by_plan_id()
        import pdb; pdb.set_trace()
        assemblies = objects.registry.Assembly.get_all_by_plan_id(plan_id)

        worker_api.API(context=self.context).perform_action(
            verb=verb,
            build_id=image.id,
            git_info=git_info,
            name=image.name,
            base_image_id=image.base_image_id,
            source_format=image.source_format,
            image_format=image.image_format,
            assembly_id=assem.id,
            test_cmd=test_cmd)

    def _create_params(self, plan_id, user_params, sys_params):
        param_obj = objects.registry.Parameter()
        param_obj.plan_id = plan_id
        if user_params:
            param_obj.user_defined_params = user_params
        if sys_params:
            param_obj.sys_defined_params = sys_params
        param_obj.create(self.context)

    def _delete_params(self, plan_id):
        param_obj = objects.registry.Parameter.get_by_plan_id(self.context,
                                                              plan_id)
        if param_obj:
            sys_params = param_obj.sys_defined_params
            if sys_params and 'REPO_DEPLOY_KEYS' in sys_params:
                # sys_params['REPO_DEPLOY_KEYS'] is just a reference to
                # deploy keys when sys_param_store is not 'database'
                if sys_param_store == 'local_file':
                    secrets_file = CONF.api.system_param_file
                    s = shelve.open(secrets_file)
                    del s[sys_params['REPO_DEPLOY_KEYS'].encode("utf-8")]
                    s.close()
                elif sys_param_store == 'barbican':
                    osc = clients.OpenStackClients(None)
                    client = osc.barbican().admin_client
                    client.secrets.delete(sys_params['REPO_DEPLOY_KEYS'])

            param_obj.destroy(self.context)
