# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Solum Worker noop handler."""

from solum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class Handler(object):
    def echo(self, ctxt, message):
        LOG.debug("%s" % message)

    def build(self, ctxt, build_id, source_uri, name, base_image_id,
              source_format, image_format, assembly_id,
              test_cmd, source_creds_ref=None):
        message = ("Build %s %s %s %s %s %s %s %s %s" %
                   (build_id, source_uri, name, base_image_id, source_format,
                    image_format, assembly_id,
                    test_cmd, (source_creds_ref or '')))
        LOG.debug("%s" % message)

    def unittest(self, ctxt, build_id, source_uri, name, base_image_id,
                 source_format, image_format, assembly_id,
                 test_cmd, source_creds_ref=None):
        message = ("Unittest %s %s %s %s %s %s %s %s %s" %
                   (build_id, source_uri, name, base_image_id, source_format,
                    image_format, assembly_id,
                    test_cmd, (source_creds_ref or '')))
        LOG.debug("%s" % message)
