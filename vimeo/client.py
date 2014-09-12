#! /usr/bin/env python
# encoding: utf-8

from functools import wraps
import requests

class VimeoClient(object):
    """Client handle for the Vimeo API."""

    API_ROOT = "https://api.vimeo.com"
    HTTP_METHODS = {'head', 'get', 'post', 'put', 'patch', 'options', 'delete'}

    def __init__(self, token=None, key=None, secret=None, *args, **kwargs):
        """Prep the handle with the authentication information."""
        self.token = BearerToken(token) if token else None
        self.app_info = (key, secret)
        self._requests_methods = dict()

        # Make sure we have enough info to be useful.
        assert token is not None or (key is not None and secret is not None)

    def __getattr__(self, name):
        """This is where we get the function for the verb that was just
        requested.

        From here we can apply the authentication information we have.
        """
        if name not in self.HTTP_METHODS:
            return

        # Get the Requests based function to use to preserve their defaults.
        request_func = getattr(requests, name, None)
        if request_func is None:
            return

        @wraps(request_func)
        def caller(url, *args, **kwargs):
            """Hand off the call to Requests."""
            return request_func(
                self.API_ROOT + url,
                auth=self.token,
                *args, **kwargs)

        return caller

class BearerToken(requests.auth.AuthBase):
    """Model the bearer token and apply it to the request."""
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer ' + self.token
        return request
