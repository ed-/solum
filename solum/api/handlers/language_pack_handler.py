# Copyright 2014 - Rackspace
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

from solum.api.handlers import handler
from solum.common import clients


class LanguagePackHandler(handler.Handler):
    """Fulfills a request on the language_pack resource."""

    def get(self, id):
        """Return a language_pack image."""
        osc = clients.OpenStackClients(self.context)
        return osc.glance().images.get(id)

    def get_all(self):
        """Return all language_packs images."""
        osc = clients.OpenStackClients(self.context)
        return osc.glance().images.list(filters={'tag': ['solum::lp']})

    def create(self, data):
        """Create a new language_pack."""
        osc = clients.OpenStackClients(self.context)
        return osc.glance().images.create(**data)

    def update(self, uuid, data):
        """Modify a language_pack."""
        osc = clients.OpenStackClients(self.context)
        return osc.glance().images.update(uuid, **data)

    def delete(self, uuid):
        """Delete a language_pack."""
        osc = clients.OpenStackClients(self.context)
        return osc.glance().images.delete(uuid)
