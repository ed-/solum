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

from solum.api.controllers.v1.datamodel import types as api_types


class Workflow(api_types.Base):
    """Representation of a Workflow.

    A workflow maintains a living creation and deployment of an App.
    """
    
    id = wtypes.text
    app_id = wtypes.text
    wf_id = int
    source = {wtypes.text: wtypes.text}
    config = {wtypes.text: wtypes.text}
    actions = {wtypes.text: wtypes.text}

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

    def as_dict(self, db_model):
        attrs = [
            'id',
            'app_id',
            'wf_id',
            'source',
            'config',
            'actions',
            ]
        base = super(Workflow, self).as_dict(db_model)
        for a in attrs:
            if getattr(self, a) is wsme.Unset:
                continue
            if getattr(self, a) is None:
                continue
            base[a] = getattr(self, a)
        return base
