**python-vimeo** is a library that wraps the
[Vimeo API v3.0](https://developer.vimeo.com/api/docs), providing
an idiomatic interface familiar to python programmers. It also
provides scripts and convenience functions that help navigate authentication,
automate uploads, and more.

Usage
-----

If you really want to become familiar with this library, read
the docstrings in the code. There is a lot of documentation with some code examples
interspersed. A good starting point would be `vimeoresource.py`.

Initialization
--------------

To start using the library, first import the `VimeoClient`

    from vimeo import VimeoClient

Then, initialize a new client with your OAuth2 access token.

    vimeo = VimeoClient("#my#access#token#")

This token can be found [here](https://developer.vimeo.com/apps), or you can
use the script included with this library to create a new one.

Creating an Access Token
------------------------

It is not strictly necessary to generate an access token before using this
library.

When using this library in the context of a web server such as Tornado, the
programmer should use the functions found in vimeo/auth.py to guide a user
through the authorization flow, allowing the user to create their own access
token. For details on guiding users through the authorization flow in the
context of a server, see the docstrings in `vimeo/auth.py`.

If you are using the library and need a new access token for yourself (for example,
for testing), there is a script provided (in `scripts/`) for offline use.

The authorization process involves asking Vimeo for an authentication token and
then using that authentication token to request the access token.

To do this offline, use the script at `scripts/authorize.py`. It requires a few
different arguments, including a list of [scopes](https://developer.vimeo.com/api/docs/auth)
requested for the newly created token.

    python authorize.py -i #my#client#id# -s #my#client#secret# -r http://mya.pp/callback/url -o public private

This script will ask you to visit a certain URL in a browser. When you have
visited the URL and clicked "Allow", you will be redirected to your app's
redirect URL. The URL will also contain a `code` parameter. Copy the body of
this parameter into the script's prompt. Once you've done this, your access
token will be automatically generated.

You can then use this access token to authenticate your `VimeoClient`
instance.

Making API Calls
----------------

All calls to the API are made via the `VimeoClient`. The hierarchy of
sub-objects is directly related to the enumeration of endpoints in the
[documentation](https://developer.vimeo.com/api/docs/endpoints). Each of the
"resource categories" (eg `/users`, `/videos`, etc) are accessible by name
from the vimeo client:

    vimeo.users(query="puppies")

The above call performs a search on `/users` with the query "puppies". The
other "resource category" roots work similarly - in fact, the majority of
endpoints in the library accept the `query` and `query_fields` kwargs.

To request a specific instance of one of these resource categories, use
typical python dot syntax for property access.

    vimeo.users.emmett9001()

This requests `/users/emmett9001`. Since `emmett9001` is a normal python
attribute, you can also request it with `getattr()`

    getattr(vimeo.users, 'emmett9001')()

The library also provides a convenience method for this behavior

    vimeo.users.get('emmett9001')()

which is equivalent to the two above calls.

Continuing down the hierarchy of endpoints, we can get a specific attribute of
our user, for example, `following`.

    vimeo.users.emmett9001.following()

This call requests `/users/emmett9001/following`. See a pattern?

Me
--

A special case is the `me` call, which is an exact behavioral equivalent
to `getattr(vimeo.users, "my username")`. This is used with simply

    vimeo.me.following()

The user that this call refers to is the owner of the access token provided at
client initialization time.

Asynchronous Operation
----------------------

The library supports synchronous calls as well as two different flavors of
asynchronous operation. These two flavors are *callbacks* and *tornado
coroutines*. They can be used interchangeably within the same program.

Examples of each use case can be found in the file `server.py`.

The library can be called as a Tornado coroutine using the `async` kwarg as follows:

    result = yield vimeo.users(query='joe', async=True)

The library can be called with a callback function as follows:

    def callback(result):
        self.write(result)
        self.finish()
    vimeo.users(query='joe', _callback=callback)

Both the `_callback` and `async` kwargs are supported by all library functions
that reference resources.

Editable Resources
------------------

It turns out that `vimeo.me.following` supports `PUT` and
`DELETE` as well as `GET`, (as do many other endpoints) which means we can make
changes to the resource located there.

To add a followee, we can use `put()`.

    vimeo.me.following.put("joelifrieri")

If we don't want to follow Joe anymore, we can use

    vimeo.me.following.delete("joelifrieri")

To see the full list of editable and non-editable resources in this library,
look at any call to `merge_properties()` in `resources.py`.

Uploads
-------

The library handles streaming uploads with a single simple call:

    vimeo.upload("/my/great/video/file.mp4", post_check_hook=my_hook)

If your access token is allowed the `upload` scope, you can use this method.

Behind the scenes, the library makes a number of requests on your behalf
(which are detailed in the docstrings in `uploads.py`). These include a call
made after uploading that checks the amount of the file that has been
successfully uploaded. You can supply a hook to the upload function. If you do
so, this hook will be called after each size check. See the docstrings in
`upload.py` for details.

Testing
-------

To run the unit tests, you need pytest

    pip install pytest

Once you have that, `cd` into the root directory of this repo and

    py.test --tb=line -vs

License
-------

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
