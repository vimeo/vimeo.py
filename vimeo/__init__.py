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
under the license.
"""

import logging as log

import resources
from uploads import Uploader
from auth import get_access_token


class VimeoClient():
    """
    Root of the vimeo API
    All API endpoints are accessible via getattr() on VimeoClient
    """
    def __init__(self, access_token=None, client_id=None, client_secret=None, dev=False):
        """
        Create an instance of VimeoClient
        Simply sets up some global configuration and allocates all attributes (API endpoints)

        Args:
        access_token (String) -- your OAuth2 access token (required)

        Kwargs:
        dev (Boolean) -- If true, the VimeoClient will make calls to api.vimeo.dev
        """
        # Global configuration used for all requests
        self.config = {
            # The access token provided at instantiation
            'access_token': access_token,
            # The client id provided at instantiation
            'client_id': client_id,
            # The secret provided at instantiation
            'client_secret': client_secret,

            # The root of all API request URLs
            'apiroot': 'https://api.vimeo.%s' % ('dev' if dev else 'com'),

            # The custom HTTP user agent string for this library
            'user-agent': 'python-vimeo 0.1; (http://developer.vimeo.com/api/docs)',

            # Run in development mode?
            'dev': dev,

            # Default "Accept" HTTP header sent with every request if none is specified
            'accept': 'application/vnd.vimeo.*+json; version=3.0'
        }

        """
        Roots of API subtrees. Most correspond to VimeoResource instances
        Each of the keys in this dictionary is used as an attribute of the instance
        Each of the values in this dictionary must be callable

        These properties are accessed via, for example,

            vimeo = VimeoClient("#####")
            vimeo.users()
        """
        self.resource_roots = dict({
            "me": self._setup_me,
            "upload": self._setup_upload
        }.items() + resources.mapper.items())

    def __dir__(self):
        return sorted(self.resource_roots.keys())

    def __repr__(self):
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def __getattr__(self, name):
        """
        Primary entry point for API request methods and subtrees

        This class defines some utility methods explicitly, but all API call methods
        are accessed via getattr()
        """
        return self.resource_roots[name](self.config)

    def _setup_me(self, config):
        """
        Lookup the current user by access token and return a new User instance
        with that user

        Called with, for example:

            vimeo = VimeoClient("#####")
            vimeo.me()

        Args:
        config (Dict) -- the global configuration dictionary
        """
        users = resources.Users(config)
        # have to actually get the current user's uri for this to work
        res = users._request_path(config, url_override="/me")
        uname = res['body']['uri'].split('/')[2]
        return resources.User(uname, users._urlpath, users.config)

    def _setup_upload(self, config):
        """
        Generate a new Uploader object

        Called with

            vimeo = VimeoClient("####")
            vimeo.upload()

        Args:
        config (Dict) -- the global configuration dictionary
        """
        return Uploader(config)

    def set_loglevel(self, loglevel):
        if hasattr(log, loglevel):
            log.basicConfig(level=getattr(log, loglevel))
        else:
            log.basicConfig(level=log.ERROR)
            log.error("Unrecognized loglevel %s, defaulting to ERROR", loglevel)

    def authenticate(self, auth_code, client_id, secret, redirect):
        """
        Generate and save an access token using public and private keys, as
        well as the authorization code.

        Args:
        auth_code   - The code query parameter returned from /oauth/authorize
        client_id   - The public client ID for the app
        secret      - The secret key for the app
        redirect    - The app redirect url
        """
        self.config['access_token'] = get_access_token(auth_code,
                                                       self.config['apiroot'],
                                                       client_id, secret, redirect)
