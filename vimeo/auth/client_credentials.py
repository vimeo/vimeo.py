#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

from .base import AuthenticationMixinBase
from . import GrantFailed

class ClientCredentialsMixin(AuthenticationMixinBase):
    """Implement the client credentials grant for Vimeo.

    This class should never be inited on it's own.
    """

    def load_client_credentials(self):
        """Retrieve a client credentials token for this app."""
        code, headers, resp = self.call_grant('/oauth/authorize/client',
            {"grant_type": "client_credentials"})

        if not code == 200:
            raise GrantFailed()

        self.token = resp['access_token']

        return self.token
