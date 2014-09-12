#! /usr/bin/env python
# encoding: utf-8

import urllib
from base import AuthenticationMixinBase
from . import GrantFailed

class AuthorizationCodeMixin(AuthenticationMixinBase):
    """Implement helpers for the Authorization Code grant for OAuth2."""

    def auth_url(self, scope, redirect):
        """Get the url to direct a user to authenticate."""
        url = self.API_ROOT + "/oauth/authorize?"

        query = {
            "response_type": "code",
            "client_id": self.app_info[0]
        }

        if scope:
            if not isinstance(scope, basestring):
                scope = ' '.join(scope)

            query['scope'] = scope

        if redirect:
            query['redirect_uri'] = redirect

        return url + urllib.urlencode(query)

    def exchange_code(self, code):
        """Perform the exchange step for the code from the redirected user."""
        # TODO.