"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from functools import partial

class VimeoResponse(dict):
    """Model a response from the Vimeo API.

    Primarily serves to provide convience methods for known references inside
    an object, like .next() and .prev() for pagination."""

    def __init__(self, resource_handle, *args, **kwargs):
        """Initialize our handle on the resource and bind functions"""
        self.resource_handle = resource_handle
        super(VimeoResponse, self).__init__(*args, **kwargs)

        # Presently there is nothing to do if we don't have a body in the response, just be a dumb dict.
        if not 'body' in self:
            return

        if 'paging' in self['body']:
            for name, url in self['body']['paging'].iteritems():
                if url:
                    self.__setattr__(name, partial(self._get_named_page, name))

    def _get_named_page(self, page, async=False, *args, **kwargs):
        """Get a specified page from the paging section of the response.

        For instance, if we have a "next" page, then we can call response._get_named_page('next') and it will retrieve it."""
        return self.resource_handle._request_path(
            self.resource_handle.config,
            url_override=self['body']['paging'][page],
            async=async)
