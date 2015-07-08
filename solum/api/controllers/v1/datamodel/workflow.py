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


import wsme
from wsme import types as wtypes

from solum.api.controllers import common_types
from solum.api.controllers.v1.datamodel import types as api_types


class Workflow(wtypes.Base):
    """Representation of a Workflow.

    A workflow maintains a living creation and deployment of an App.
    """

    uri = common_types.Uri
    "URI to the resource."

    uuid = wtypes.text
    "Unique Identifier of the resource"

    type = wtypes.text
    "The resource type."
    
    id = wtypes.text
    app_id = wtypes.text
    wf_id = int
    source = {wtypes.text: wtypes.text}
    config = {wtypes.text: wtypes.text}
    actions = [wtypes.text]

    def __init__(self, *args, **kwargs):
        super(Workflow, self).__init__(*args, **kwargs)

    @classmethod
    def sample(cls):
        return cls(
            wf_id=1,
            config={},
            actions={},
            source={},
            )

    @classmethod
    def from_db_model(cls, m, host_url):
        json = m.as_dict()
        json['type'] = m.__tablename__
        json['uri'] = ''
        json['uri'] = ('%s/v1/apps/%s/workflows/%s' %
                       (host_url, m.app_id, m.wf_id))
        return cls(**(json))

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)

    def as_dict(self, db_model):
        valid_keys = [attr for attr in db_model.__dict__.keys()
                      if attr[:2] != '__' and attr != 'as_dict']
        base = self.as_dict_from_keys(valid_keys)
        attrs = [
            'id',
            'app_id',
            'wf_id',
            'source',
            'config',
            'actions',
            ]
        for a in attrs:
            if getattr(self, a) is wsme.Unset:
                continue
            if getattr(self, a) is None:
                continue
            base[a] = getattr(self, a)
        return base
