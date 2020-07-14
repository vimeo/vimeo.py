# <img src="https://user-images.githubusercontent.com/33762/33720344-abc20bb8-db31-11e7-8362-59a4985aeff0.png" width="250" />

[![PyPi](https://img.shields.io/pypi/v/PyVimeo.svg?style=flat-square)](https://pypi.python.org/pypi/PyVimeo/)
[![License](https://img.shields.io/pypi/l/PyVimeo.svg?style=flat-square)](https://pypi.python.org/pypi/PyVimeo/)

This is a simple Python library for interacting with the [Vimeo API](https://developers.vimeo.com).

- [Get Started](#get-started-with-the-vimeo-api)
- [Help](#direct-help)
- [Troubleshooting](#troubleshooting)
- [Installation](#installation)
- [Usage](#usage)
    - [Authentication and access tokens](#authentication)
        - [Unauthenticated tokens](#unauthenticated)
        - [Authenticated tokens](#authenticated)
    - [Make requests](#make-requests)
    - [Uploading videos](#uploading-videos)
        - [Uploading a new video](#uploading-a-new-video)
        - [Replacing a video source file](#replacing-a-video-source-file)
    - [Upload images](#upload-images)
    - [Upload a text track](#upload-a-text-track)

## Get started with the Vimeo API

There is a lot of information about the Vimeo API at <https://developer.vimeo.com/api/start>. Most of your questions are answered there!

## Direct Help

 * [Stack Overflow](http://stackoverflow.com/questions/tagged/vimeo-api)
 * [Vimeo Support](https://vimeo.com/help/contact)

## Installation

This package is called [PyVimeo](https://pypi.python.org/pypi/PyVimeo/) on PyPI. Install using:

    pip install PyVimeo

## Usage
```python
import vimeo

v = vimeo.VimeoClient(
    token=YOUR_ACCESS_TOKEN,
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET
)

# Make the request to the server for the "/me" endpoint.
about_me = v.get('/me')

# Make sure we got back a successful response.
assert about_me.status_code == 200

# Load the body's JSON data.
print about_me.json()
```

*Note: You can find the app tokens and an authenticated bearer token in the OAuth 2 tab for your app on the [Vimeo developer site](https://developer.vimeo.com/apps).*

### Authentication

There are two main types of authentication in the Vimeo API:

- [Unauthenticated](#unauthenticated) - Access tokens without a user. These tokens can view only public data.
- [Authenticated](#authenticated) - Access tokens with a user. These tokens interact on behalf of the authenticated user.

*Note: Both types of authentication require you go to the [Vimeo developer site](https://developer.vimeo.com/apps) and register an application with Vimeo.*

#### Unauthenticated

Unauthenticated API requests must generate an access token. You should not generate a new access token for each request. Instead, request an access token once and use it forever.

```python
try:
    # `scope` is an array of permissions your token needs to access.
    # You can read more at https://developer.vimeo.com/api/authentication#supported-scopes
    token = v.load_client_credentials(scope)

    # usable access token
    print 'token=%s' % token
except vimeo.auth.GrantFailed:
    # Handle the failure to get a token from the provided code and redirect.
```

#### Authenticated

Getting a bearer token via the authorization code method is a bit more involved. Here are the basic steps:

1. We send the user to a web page where they can choose to accept or reject the permissions we are asking for.
2. When the user makes their selection and accepts or rejects your app, the user is redirected to a webpage specified by you.
3. If the user authorized your app, you can exchange the provided code for the bearer token.

This can be done with this library using some basic helper functions, as the following code demonstrates. Notice that there are two sections: first, where you redirect the user to Vimeo; and second, where the user returns so that you can perform the final step.

```python
"""This section is used to determine where to direct the user."""
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET
)

vimeo_authorization_url = v.auth_url(
    ['public', 'private'],
    'https://example.com'
)

# Your application should now redirect to `vimeo_authorization_url`.
```

```python
"""This section completes the authentication for the user."""
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET
)

# You should retrieve the "code" from the URL string Vimeo redirected
# to. Here, that's named `CODE_FROM_URL`.
try:
    token, user, scope = v.exchange_code(CODE_FROM_URL, 'https://example.com')
except vimeo.auth.GrantFailed:
    # Handle the failure to get a token from the provided code and redirect.

# Store the token, scope and any additional user data you require in
# your database so users do not have to re-authorize your application
# repeatedly.
```

This process is straightforward in theory, but it does require a little more effort than the client credentials grant to make work properly. Remember that you may ask for scopes that the user decides *not* to give you, and your application must gracefully handle that.

### Make requests

PyVimeo at its core is a wrapper for [Requests](http://docs.python-requests.org/en/master/), so you can interact with the library as you would any other object from Requests.

* **GET:** `response = v.get(uri)`, or with parameters `v.get(uri, data={...})`
* **PATCH:** `response = v.patch(uri, data={...})`
* **POST:** `response = v.post(uri, data={...})`
* **PUT:** `response = v.put(uri, data={...})`
* **DELETE:** `response = v.delete(uri)`

#### JSON Filtering

The Vimeo API supports [JSON filtering](https://developer.vimeo.com/api/common-formats#json-filter) to let you return only the data that you need from an API call. To utilize this with PyVimeo, you can add a `fields` variable into your endpoint payload, like:

```python
about_me = v.get('/me', params={"fields": "uri,name,pictures"})
```

Then with this response, you will receive only `uri`, `name`, and the `pictures` object.

### Uploading videos
#### Uploading a new video

Once you have an authenticated instance of the `VimeoClient` class, uploading is a single function call away with `upload`. Internally, this library provides the `tus` upload and sends a local file to the server with the [tus](https://tus.io/) upload protocol and [tus-python-client](https://github.com/tus/tus-py-client).

```python
video_uri = v.upload('your-filename.mp4')
```

If you wish to add metadata to your video as it's being uploaded, you can supply a `data` object to `.upload()`.

```python
video_uri = v.upload(
    'your-filename.mp4',
    data={'name': 'Video title', 'description': '...'}
)
```

Alternatively, you can do this after the video has been uploaded with a PATCH call.

```python
video_uri = v.upload('your-filename.mp4')

v.patch(video_uri, data={'name': 'Video title', 'description': '...'})
```

#### Replacing a video source file

Once you have an authenticated instance of the `VimeoClient` class, you can also replace the source file of an existing video.

```python
video_uri = v.replace(
    video_uri='video_uri',
    filename='your-filename.mp4'
)
```

### Upload images

Once you have an authenticated instance of the `VimeoClient` class, uploading a picture requires only the target object (for instance, the video for which you would like to replace the thumbnail).

```python
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET
)

v.upload_picture('/videos/12345', 'your-image.jpg', activate=True)
```

Note: The `activate=True` in `v.upload_picture` sets this picture as the active one for all users. The `activate` keyword argument defaults to `False`, so without it you need to activate the picture yourself.

### Upload a text track

Once you have an authenticated instance of the `VimeoClient` class, uploading a text track requires the video URI of the video the text track will be added to, text track type, text track language, and text track filename.

```python
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET
)

v.upload_texttrack('/videos/12345', 'captions', 'en-US', 'your-texttrack.vtt')
```

## Troubleshooting

If you have any questions or problems, create a [ticket](https://github.com/vimeo/vimeo.php/issues) or [contact us](https://vimeo.com/help/contact).

## Legacy Python Library

An earlier version of this library used a different, more involved ORM syntax. This library is still available from this GitHub repo via the [orm-tornado](https://github.com/vimeo/vimeo.py/releases/tag/orm-tornado) tag.
