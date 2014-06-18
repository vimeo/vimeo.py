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
import json
import os
from urllib import urlencode
import logging as log
import base64
from functools import partial

from tornado.httpclient import AsyncHTTPClient, HTTPClient
import tornado
import tornado.gen

import resources
import vimeoresponse

log.basicConfig(level=log.WARNING)

def async(func):
    @tornado.gen.coroutine
    def inner(*args, **kwargs):
        log.info("Async call arguments were: %s, %s" % (args, kwargs))
        raise tornado.gen.Return(func(*args, **kwargs))
    return inner

class VimeoResource(object):
    """
    A "plural" root of an API subtree (eg VimeoClient.users)
    Also the base class of a generic RESTful Vimeo API resource

    This is the base class used to represent "thing" concepts in the Vimeo
    API. For example, a video, user, or album are all represented as subclasses
    of VimeoResource.

    The class is plural in the sense that it will refer to a group of
    resources (/users, /videos) as opposed to a single resource (/users/34)
    """
    properties = None

    def __init__(self, config, urlpath="", properties={}):
        """
        Simply sets the config and the urlpath

        urlpath is the url segment corresponding to this resource type.
        For example, if this VimeoResource is Users, urlpath will be /users.

        Args:
        config (Dict) -- the global configuration dictionary
        """
        self._urlpath = urlpath
        self._singular = None
        self.config = config
        self.accept = "*"
        self.properties = properties

    def __getattr__(self, name):
        """
        Get a "singular" version of this resource type (SingularResource)
        For example, if this is a Users object, __getattr__ accepts the identifier
        of a specific user. This allows calls like

            vimeo.users.emmett9001()

        There is a special case:

            vimeo.users.1234567()

        is a python syntax error since it starts with a number. To get around this,
        we first check if the literal name is valid with the API. If not, we strip
        special marker characters and retry. This allows the above call to be made as

            vimeo.users.u1234567()
        or
            getattr(vimeo.users, 1234567)
        or
            vimeo.users.get(1234567)
        """
        name = str(name)

        # special case for POST requests
        if name == 'post':
            def _do_post(data, _callback=None):
                return self._request_path(self.config, querys=data, method="POST", async=async, _callback=_callback)
            return _do_post

        # the normal cases, in which we're getting a subresource
        try:
            # perform an API call to see if the resource exists at `name`
            #self._singular(name, self._urlpath, self.config, properties=self.properties)()
            pass
        except:
            # if not, strip our special characters
            name = name.strip("eucgvpa")
        name = name.split('/')[-1]
        return self._singular(name, self._urlpath, self.config, properties=self.properties)

    def __str__(self):
        """
        Let a VimeoResource's string representation be the url at which it is
        located.
        """
        return self._urlpath

    def _build_parameters(self, query=None, query_fields=[], _filter=None,
                          sort=None, reverse=False, content_filter=None,
                          page=0, per_page=0, capabilities={}):
        """
        Monolithic handler for all query parameters allowed by the API.
        Sets the following querystring arguments, if applicable:

        query, query_fields
        filter
        sort, direction
        content_filter
        page, per_page

        Certain SingularResource instances may or may not have search, filter, or sort
        capabilities. These differences, if present, are handled in SingularResource

        Args:
        query (String)          -- The search query
        query_fields (String)   -- The field to query against while searching
        _filter (String)        -- The filter query
        sort (String)           -- The sort key for returned results
        reverse (Boolean)       -- If True, requests are made with descending sort
        content_filter (String) -- The content filtering level
        page (Number)           -- The page of data to return
        per_page (Number)       -- The page size to return
        """
        params = {}
        if not capabilities or capabilities['search']:
            params['query'] = query
            params['query_fields'] = ' '.join(query_fields)
        if not capabilities or capabilities['filter']:
            params['filter'] = _filter
        if not capabilities or capabilities['sort']:
            params['sort'] = sort
            if sort:
                params['direction'] = 'desc' if reverse else 'asc'
        params['content_filter'] = content_filter
        params['page'] = str(page) if page else ''
        params['per_page'] = str(per_page) if per_page else ''
        return params

    def get(self, identifier):
        """
        Convenience method for accessing SingularResources

        Used as

            vimeo.users.get(1234567)()

        This method can be used interchangeably with the other
        SingularResource accessors (vimeo.users.u1234567(), for example)

        Args:
        identifier (String, Number) -- Unique identifier for the resource
        """
        return getattr(self, identifier)

    def _request_path(self, config, _callback=None, async=False, method="GET", endpoint='', body=None, querys={},
                      url_override='', extra_headers={}):
        """
        Make a request to the Vimeo API

        Most of the values returned from API accessor methods (for example,
        the return value of vimeo.users.emmett9001) is callable. Calling the
        return value as

            vimeo.users.emmett9001()

        results in a call to this method.

        Can be synchronous or asynchronous (with a callback or as a coroutine).
        If a callback is used, it should accept two parameters: the response JSON
        as a dictionary, and the request error if any. For example:

            def handle_response(response, error):
                if not error:
                    print response['data'][0]['uri']
                else:
                    raise ValueError(error.text)

        If a callback argument is not specified, the request made *will* be blocking

        Args:
        config (Dict)   -- The global configuration dictionary

        Kwargs:
        _callback (Function)    -- If specified, an asynchronous request is performed
        async (Boolean)         -- If True, the result will be returned to the top
                                   level caller inside of a Future
        method (String)         -- The HTTP method to use in the request
        endpoint (String)       -- Used in combination with self._urlpath to build path
                                   Also indexes into the subclass' properties dictionary
        body (String)           -- The request body
        querys (Dict)           -- The querystring arguments to send
        url_override(String)    -- Completely overrides the path set by endpoint.
                                   Currently only used for the /me endpoint
        extra_headers(Dict)     -- A dictionary of HTTP headers that will be
                                   used in addition to the headers provided by this
                                   library
        """
        accept = "*"
        if hasattr(self, 'properties'):
            if endpoint in self.properties and 'accept' in self.properties[endpoint]:
                accept = self.properties[endpoint]['accept']
        elif hasattr(self, 'accept'):
            accept = self.accept

        headers = {"Accept": 'application/vnd.vimeo.%s+json; v3.0' % accept,
                   "User-Agent": config['user-agent']}

        # HTTPClient doesn't like when requests with these methods have bodies
        # that aren't strings
        if method in ["PUT", "POST", "PATCH"] and not body:
            body = ''

        # If an overriding URL is given, use only it
        if url_override:
            url = "%s%s" % (config['apiroot'], url_override)
        # otherwise, concatenate the existing urlpath and the given endpoint
        # to create the request URL
        else:
            url = "%s%s/%s" % (config['apiroot'], self._urlpath, endpoint.split('/')[-1])
        url = self._append_querystring(url, querys)

        url,headers = self._set_auth_markers(url, headers)
        # add additional headers to the request if they were given
        headers = dict(headers.items() + extra_headers.items())

        log.info("%s %s" % (method, url))
        log.info(headers)
        log.info(body)

        # fork for an asynchronous or synchronous request
        if _callback and not async:
            def __callback(response):
                result = self._parse_response_body(response.body, headers=response.headers)
                _callback(result, response.error)
                self._end_request_handler(result, response.error)

            AsyncHTTPClient().fetch(url,
                __callback, method=method, headers=headers,
                validate_cert=not self.config['dev'], body=body)
            log.info("IOLoop running: %s" % tornado.ioloop.IOLoop.instance()._running)
            self._should_stop_ioloop_on_finish = True
            if tornado.ioloop.IOLoop.instance()._running:
                self._should_stop_ioloop_on_finish = False
            else:
                tornado.ioloop.IOLoop.instance().start()
            return
        else:
            result = HTTPClient().fetch(url, method=method, headers=headers,
                                        validate_cert=not self.config['dev'], body=body)
            return self._parse_response_body(result.body, headers=result.headers)

    def _set_auth_markers(self, url, headers):
        """
        Use the supplied app identifiers to try and authenticate the request.
        First try access token. If that doesn't exist, try using the b64 encoded
        combination of the client id and client secret for basic auth.
        Failing that, try sending the client ID in the querystring.
        Otherwise, return the unaltered url and headers and get ready for a 401

        The keys 'access_token', 'client_id', and 'client_secret' can be supplied
        in the `config` dictionary. These strings can also be specified via
        environment variables: VIMEO_ACCESS_TOKEN, VIMEO_CLIENT_ID, and
        VIMEO_CLIENT_SECRET. These variables can be assigned on linux with

            export VIMEO_CLIENT_ID=my#client#id

        Args:
        url     - The request url, with or without a querystring
        headers - The dictionary of request headers

        Returns a url,headers tuple containing the altered url and headers
        """
        headers = headers.copy()
        access_token = os.environ.get('VIMEO_ACCESS_TOKEN', self.config['access_token'])
        client_id = os.environ.get('VIMEO_CLIENT_ID', self.config['client_id'])
        client_secret = os.environ.get('VIMEO_CLIENT_SECRET', self.config['client_secret'])
        if access_token:
            headers["Authorization"] = "bearer %s" % access_token
        elif client_id and client_secret:
            encoded = base64.b64encode("%s:%s" % (client_id, client_secret))
            headers["Authorization"] = "basic %s" % encoded
        elif client_id:
            if "?" in url:
                url += "&client_id=%s" % client_id
            else:
                url += "?client_id=%s" % client_id
        return url,headers

    def _append_querystring(self, url, querys):
        """
        Utility: takes a url and a querystring dict, returns a constructed URL

        If the url already includes a querystring, it is replaced

        Args:
        url (String)    -- The url to which querystring will be appended
        querys (Dict)   -- The dictionary representing the querystring arguments
        """
        if not querys: return url
        if "?" in url:
            url = url.split('?')[0]
        url = "%s?" % url
        querys = {a: querys[a] for a in querys if querys[a]}
        url += urlencode(querys)
        return url

    def _end_request_handler(self, response, error):
        """
        Helper, called once an asynchronous request ends

        Stops the IOLoop that was started when the async request was
        initialized

        Args:
        response (Dict) -- Dictionary representing the returned JSON
        error           -- The request error, if any
        """
        log.info("Should stop ioloop: %s" % self._should_stop_ioloop_on_finish)
        if self._should_stop_ioloop_on_finish:
            tornado.ioloop.IOLoop.instance().stop()

    def _parse_response_body(self, body, headers={}):
        """
        Utility: parse the body of a JSON response as a dictionary

        Args:
        body (String)   -- The JSON string to parse
        """
        ret = {'headers': headers}
        if body:
            ret['body'] = json.loads(body)

        return vimeoresponse.VimeoResponse(self, ret)

    def _cat_url_path(self, urlpath):
        """
        Concatenate this object's urlpath with the passed path.

        This is used to create nested relationships between resources.
        For example, self._urlpath might be `/users/emmett9001` and urlpath
        might be /videos/1234567. This would result in the new, concatenated
        path

            /users/emmett9001/videos/1234567

        Args:
        urlpath (String) -- The url path to concatenate with the existing path
        """
        if self._urlpath:
            self._urlpath += urlpath
        else:
            self._urlpath = urlpath


class CallableVimeoResource(VimeoResource):
    """
    Subclass of VimeoResource that adds callable functionality

    The only plural resource class that does not inherit from this class
    is Albums
    """
    @async
    def _call__(self, _callback=None, async=False, **kwargs):
        """
        Perform an HTTP GET request on the root of this subtree
        This method is wrapped by __call__ and returns a Future

        Example use:

            vimeo.users(query="puppies")

        Args:
        _callback (Function)    -- passed to _request_path
        async (Boolean)         -- If True, the result will be returned to the top
                                   level caller inside of a Future

        Kwargs:
        See VimeoResource._build_parameters()
        """
        params = self._build_parameters(**kwargs)
        return self._request_path(self.config, async=async, _callback=_callback, querys=params)

    def __call__(self, async=False, **kwargs):
        """
        Decide based on the `async` kwarg whether to return a Future or wait for the
        Future to complete and then return the raw result.

        The former is used with tornado.gen.coroutine and a `yield` statement.
        The latter is used when calling the library synchronously

        Kwargs:
        async (Boolean)     -- If True, the result of _call__ is returned wrapped
                               in a Future
        """
        log.info("Async: %s" % async)
        ret = self._call__(async=async, **kwargs)
        if async:
            return ret
        else:
            # wait for the future to finish, then return synchronously
            # can't use tornado.ioloop.IOLoop.instance().run_sync() since it
            # stops the IOLoop upon completion
            while not ret.done():
                pass
            return ret.result()


class SingularResource(VimeoResource):
    """
    A "singular" node in the API subtree. (eg VimeoClient.users.emmett9001)
    """
    def __init__(self, name, path, config, properties={}):
        """
        Sets important fields and the configuration

        The properties dictionary indicates the methods allowed on a particular
        subclass, and follows a particular format. Keys are the method names
        allowed (corresponding to the endpoints of the same name). Values are
        themselves dictionaries with multiple allowed keys:

        search (Boolean)     -- Is this resource searchable
        sort (Boolean)       -- Is this resource sortable
        filter (Boolean)     -- Is this resource filterable
        accept (String)      -- The type of vimeo resource to accept in a response
        methods (List)       -- List of string HTTP methods (eg ["GET"])
        subresources (Dict)  -- A dictionary structured the same way as the
                                properties dictionary itself that contains valid
                                subresources of the resource
        single_get (Boolean) -- Indicates that the resource responds to GET
                                requests only for individual subresources
        multi_put (Boolean)  -- Indicates that the resource responds to PUT
                                requests only when they contain lists of items
                                See PutMultiResourceEditor for details

        See resources.py for examples of the `properties` dictionary.

        Args:
        name (String)   -- The unique identifier for this resource (eg "emmett9001")
        path (String)   -- The preceeding part of the URL path, inherited from the parent class
        config (Dict)   -- The global configuration dictionary
        """
        self._identifier = name
        self._urlpath = "%s/%s" % (path, name)
        self.config = config
        self.accept = "*"
        self.properties = properties  # not the best design since a lot of this class
                              # expects properties to be implemented a certain way

    def __dir__(self):
        return sorted(self.properties.keys())

    @async
    def _call__(self, _callback=None, async=False, **kwargs):
        """
        Perform an HTTP GET request for this resource
        This method is wrapped by __call__ and returns a Future

        Example usage:

            vimeo.users.emmett9001()


        Kwargs:
        _callback (Function)    -- passed to _request_path
        async (Boolean)         -- If True, the result will be returned to the top
                                   level caller inside of a Future
        See VimeoResource._build_parameters()
        """
        params = self._build_parameters(**kwargs)
        return self._request_path(self.config, _callback=_callback, async=async, querys=params)

    def __call__(self, async=False, **kwargs):
        """
        Decide based on the `async` kwarg whether to return a Future or wait for the
        Future to complete and then return the raw result.

        The former is used with tornado.gen.coroutine and a `yield` statement.
        The latter is used when calling the library synchronously

        Kwargs:
        async (Boolean)     -- If True, the result of _call__ is returned wrapped
                               in a Future
        """
        log.info("Async: %s" % async)
        ret = self._call__(async=async, **kwargs)
        if async:
            return ret
        else:
            # wait for the future to finish, then return synchronously
            # can't use tornado.ioloop.IOLoop.instance().run_sync() since it
            # stops the IOLoop upon completion
            while not ret.done():
                pass
            return ret.result()

    def __getattr__(self, name):
        """
        Call a method on this resource

        What happens in this method is fairly subclass-specific, and is defined in
        any SingularResource subclass. This method reads the API calls available for
        the object's type via the `properties` dictionary (for example, it sees
        that a User object can call videos())
        """
        # The properties must be known in order for thie method to work
        if name is '_should_stop_ioloop_on_finish':
            return

        if not self.properties:
            raise ValueError, "Resource properties not defined"

        def _make_requester(method, endpoint=""):
            def _do_request(data=None, _callback=None, async=False, **kwargs):
                params = {}
                if name not in ["patch", "delete"]:
                    params = self._build_parameters(capabilities=self._get_capabilities(name),
                                                    **kwargs)

                kwargs = {
                    '_callback': _callback,
                    'async': async,
                    'method': method,
                    'endpoint': endpoint
                }

                if name in {"patch", "post"}:
                    kwargs['extra_headers'] = {'Content-Type': 'application/json'}
                    kwargs['body'] = json.dumps(data or params)
                else:
                    kwargs['querys'] = data or params
                return self._request_path(self.config, **kwargs)
            return _do_request

        method_mapper = {
            "DELETE": ResourceEditor,
            "POST": PostPatchResourceEditor,
            "PATCH": PostPatchResourceEditor,
            "PUT": PutResourceEditor
        }

        # return a ResourceEditor subclass based on the information found in
        # `properties`
        if self.prop_is_true(name, 'multi_put'):
            return PutMultiResourceEditor(name, self._urlpath, self.config,
                                          self._get_capabilities(name), self.properties)
        if self.prop_is_true(name, 'single_get'):
            return ResourceEditor(name, self._urlpath, self.config,
                                  self._get_capabilities(name), self.properties)
        for method in method_mapper.keys():
            # If the attribute we're getting is an editing method, just perform it
            if name == method.lower():
                if method in self.methods:
                    return _make_requester(method)
            else:
                # The attribute might be editable, so return the proper editor
                if method in self.properties.get(name, {'methods': []})['methods']:
                    return method_mapper[method](name, self._urlpath, self.config,
                                                 self._get_capabilities(name), self.properties)

        # Maybe the attribute should be treated as a subresource
        # in which case we should instantiate and return that subresource
        has_subresources = 'subresources' in self.properties[name].keys()
        if has_subresources or self.prop_is_true(name, 'resource'):
            properties = {}
            if has_subresources:
                # allow arbitrary nesting of properties dicts for subresources
                # by creating a new instance of the subresource class and
                # returning it
                properties = self.properties[name]['subresources']
            return resources.mapper[name](self.config, urlpath=self._urlpath, properties=properties)

        # If none of the above are true, just do a GET request for the resource
        return _make_requester("GET", endpoint=name)

    def _get_capabilities(self, name):
        """
        Helper: Construct a dictionary indicating the querying capabilities for a
        given API method

        Args:
        name (String)   -- The method being examined
        """
        def _has_capability(name, capability):
            if capability in self.properties[name].keys():
                return self.properties[name][capability] == True
            return True
        capabilities = {}
        capabilities['search'] = _has_capability(name, 'search')
        capabilities['filter'] = _has_capability(name, 'filter')
        capabilities['sort'] = _has_capability(name, 'sort')
        return capabilities

    def prop_is_true(self, name, prop):
        """
        Helper: return true if the property is both defined for the name and
        is True
        """
        if prop in self.properties.get(name, {}).keys():
            if self.properties.get(name, {}).get(prop, False) == True:
                return True
        return False

    def merge_properties(self, props):
        """
        Helper: Merge the regular and subresource properties, giving precedence to
        the subresource ones (allowing the subresource settings to override
        the defaults).

        This is used when a subresource is instantiated for a resource. For
        example, when accessing /users/1234567/portfolios/1234567, the
        Portfolio SingularResource class is instantiated. This class contains
        its own definition of the `properties` dictionary. The `properties` for
        User also contains a `subresources` entry for portoflios. When
        creating the Portfolio instance that is returned to the client, we
        need to ensure that it has all the valid properties of a normal
        Portfolio instance as well as those of the declared subresource.

        Put another way, we want to have the following two resource types be
        treated as similarly as possible:
            * The Portfolio class
            * The Portfolio class as accessed via the User subresource

        This method does that by merging the explicitly stated subresource
        properties of User.properties['portfolio'] with those of the Portfolio
        class, giving precedence to those in the subresource declaration.
        """
        if not self.properties:
            self.properties = props
            return
        for key in props.keys():
            if key not in self.properties.keys():
                self.properties[key] = {}
                for subkey in props[key].keys():
                    if subkey not in self.properties[key].keys():
                        self.properties[key][subkey] = props[key][subkey]


class ResourceEditor(SingularResource):
    """
    A class modeling the basic HTTP editing methods supported by resources
    """
    def __init__(self, name, path, config, capabilities, properties):
        self._identifier = name
        self._urlpath = "%s/%s" % (path, name)
        self.capabilities = capabilities
        self.config = config
        self.properties = properties

    @async
    def _call__(self, _callback=None, async=False, **kwargs):
        """
        Perform an HTTP request for this resource.
        This method is wrapped by __call__ and returns a Future

        Example usage:

            vimeo.users.emmett9001.following()

        Kwargs:
        _callback (Function)    -- passed to _request_path
        async (Boolean)         -- If True, the result will be returned to the top
                                   level caller inside of a Future
        See VimeoResource._build_parameters()
        """
        params = self._build_parameters(capabilities=self.capabilities, **kwargs)
        return self._request_path(self.config, _callback=_callback, async=async, querys=params)

    def __call__(self, async=False, **kwargs):
        """
        Decide based on the `async` kwarg whether to return a Future or wait for the
        Future to complete and then return the raw result.

        The former is used with tornado.gen.coroutine and a `yield` statement.
        The latter is used when calling the library synchronously

        Kwargs:
        async (Boolean)     -- If True, the result of _call__ is returned wrapped
                               in a Future
        """
        log.info("Async: %s" % async)
        ret = self._call__(async=async, **kwargs)
        if async:
            return ret
        else:
            # wait for the future to finish, then return synchronously
            # can't use tornado.ioloop.IOLoop.instance().run_sync() since it
            # stops the IOLoop upon completion
            while not ret.done():
                pass
            return ret.result()

    def delete(self, name, _callback=None):
        self._request_path(self.config, endpoint=name, _callback=_callback, async=async,
                method="DELETE")

    def get(self, name, _callback=None):
        return self._request_path(self.config, endpoint=name, _callback=_callback, async=async,
                method="GET")


class PutResourceEditor(ResourceEditor):
    """
    In most cases, this editor is used for resources such as /videos/#id/tags/+tag
    that support PUT of one subresource or attribute at a time.
    """
    def put(self, name, _callback=None):
        self._request_path(self.config, endpoint=name, _callback=_callback, async=async,
                method="PUT")


class PutMultiResourceEditor(PutResourceEditor):
    """
    Resource editor that supports PUT with a JSON-encoded body on a
    property

    Used only on resources marked with "multi_put": True in the properties
    dictionary

    putmulti() is currently used in only two cases:

    * /videos/#id/tags PUT
        accepts a request body containing a JSON encoded list of new tags for the
        video. Thus, the request is made without an "endpoint" parameter to allow a
        PUT action on the root /tags resource.
    * /users/#id/watchlater PUT
        accepts a request body containing a JSON encoded list of video IDs to
        be added to the user's watchlater queue.
    """
    def putmulti(self, data, _callback=None):
        extra_headers = {"Content-Type": "application/json"}
        self._request_path(self.config, body=json.dumps(data), _callback=_callback, async=async,
                method="PUT", extra_headers=extra_headers)


class PostPatchResourceEditor(ResourceEditor):
    """
    Resource editor that supports POST and PATCH requests
    """
    def post(self, params={}, _callback=None):
        self._request_path(self.config, querys=params, _callback=_callback, async=async,
                method="POST")

    def patch(self, name, params={}, _callback=None):
        self._request_path(self.config, endpoint=name, querys=params, _callback=_callback, async=async,
                method="PATCH")
