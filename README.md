PyVimeo
===

[![Development Version](https://img.shields.io/pypi/v/PyVimeo.svg?style=flat-square)](https://pypi.python.org/pypi/PyVimeo/)
[![License](https://img.shields.io/pypi/l/PyVimeo.svg?style=flat-square)](https://pypi.python.org/pypi/PyVimeo/)

This is a simple library for interacting with the [Vimeo API](https://developers.vimeo.com).

## Installation

This package is called [PyVimeo](https://pypi.python.org/pypi/PyVimeo/) on PyPI. Install using:

    $ pip install PyVimeo

## Usage
```python
import vimeo

v = vimeo.VimeoClient(
    token=YOUR_ACCESS_TOKEN,
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

# Make the request to the server for the "/me" endpoint.
about_me = v.get('/me')

assert about_me.status_code == 200  # Make sure we got back a successful response.
print about_me.json()   # Load the body's JSON data.
```

*Note: You can find the app tokens and an authenticated bearer token in the "OAuth2" tab for your app on the [Vimeo developer site](https://developer.vimeo.com/apps).*

### Authentication

There are two main types of authentication in the Vimeo API:

1. Client Credentials: A token that is specific to your app and **not** a user.
2. Authorization Code: A token that is for your app, but has the ability to act on behalf of the authorizing user.

*Note: Both types of authentication require you go to the [Vimeo developer site](https://developer.vimeo.com/apps) and register an application with Vimeo.*

#### Client Credentials

Retrieving a set of client credentials in this library is very, very easy. You must provide the `VimeoClient` with the `key` and `secret` for your app, and make a single call. The example below contains all the necessary steps. At the end of it, the `VimeoClient` instance (the variable `v`) will be authenticated with the token, and you can store the value - returned by the `load_client_credentials()` call - in your database or a file to use like the example at the start of this README.

```python
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

try:
    token = v.load_client_credentials()
except vimeo.auth.GrantFailed:
    # Handle the failure to get a token from the provided code and redirect.
```

#### Authorization Code

Getting a bearer token via the authorization code method is a bit more complicated. The most important thing to understand is that we need to go through a series of basic steps:

1. We send the user to a web page where they can choose to accept or reject the permissions we are asking for.
2. When the user makes their selection and accepts or rejects your app, the user is redirected to a webpage specified by you.
3. If the user authorized your app, you can exchange the code provided for the bearer token.

This can be done with this library using some basic helper functions. The code below demonstrates, but do note that there are 2 sections, where you redirect the user to Vimeo, and where the user returns so you can perform the final step.

```python
"""This section is used to determine where to direct the user."""
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

vimeo_authorization_url = v.auth_url(['public', 'private'], 'https://example.com')

# Your application should now redirect to vimeo_authorization_url.
```

```python
"""This section completes the authentication for the user."""
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

# You should retrieve the "code" from the URL string Vimeo redirected to. Here, that's named `CODE_FROM_URL`.
try:
    token, user, scope = v.exchange_code(CODE_FROM_URL, 'https://example.com')
except vimeo.auth.GrantFailed:
    # Handle the failure to get a token from the provided code and redirect.

# Store the token, scope and any additional user data you require in your database so users do not have to re-authorize your application repeatedly.
```

This process is generally quite simple, but it does require a little more effort than the client credentials grant to make work properly. Remember that you may ask for scopes that the user decides *not* to give you, and your application must gracefully handle that.

### Uploading a new video

Once you have an authenticated instance of the `VimeoClient` class, uploading is a single function call away. Internally, this library will provide the `streaming` upload and send a local file to the server.

After a file has been uploaded, you can edit its metadata right away with `patch`.

```python
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

video_uri = v.upload('your-filename.mp4')

v.patch(video_uri, data={'name': 'Video title', 'description': '...'})
```

##### Replacing a video source file

Once you have an authenticated instance of the `VimeoClient` class, you can also replace the source file of an existing video.

```python
video_uri = v.replace(
    video_uri='video_uri',
    filename='your-filename.mp4',
    upgrade_to_1080=False)
```

### Uploading a picture

Once you have an authenticated instance of the `VimeoClient` class, uploading a picture requires only the target object (for instance, the video for which you would like to replace the thumbnail).

```python
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

v.upload_picture('/videos/12345', 'your-image.jpg', activate=True)
```

Note: This will make it the active picture for all users this way. The `activate` keyword argument defaults to `False`, so without it you will need to activate the picture yourself.

### Uploading a text track

Once you have an authenticated instance of the `VimeoClient` class, uploading a text track requires the video uri of the video the text track will be added to, text track type, text track language, and text track filename.

```python
v = vimeo.VimeoClient(
    key=YOUR_CLIENT_ID,
    secret=YOUR_CLIENT_SECRET)

v.upload_texttrack('/videos/12345', 'captions', 'en-US', 'your-texttrack.vtt')
```

### Making API calls

PyVimeo at its core is a wrapper for [Requests](http://docs.python-requests.org/en/master/), so you can interact with the library as you sould any other object from Requests.

* **GET:** `response = v.get(uri)`, or with parameters `v.get(uri, data={...})`
* **PATCH:** `response = v.patch(uri, data={...})`
* **POST:** `response = v.post(uri, data={...})`
* **DELETE:** `response = v.delete(uri)`

### JSON Filtering

The Vimeo API supports [JSON filtering](https://developer.vimeo.com/api/common-formats#json-filter) to let you return only the data that you need from an API call. To utilize this with PyVimeo, you can add a `fields` variable into your endpoint payload, like:

```python
about_me = v.get('/me', params={"fields": "uri,name,pictures"})
```

Then with this response, you will only receive `uri`, `name`, and the `pictures` object.

## Legacy Python Library

An earlier version of this library used a more complicated ORM syntax. This library is still available from this github repo via the [orm-tornado](https://github.com/vimeo/vimeo.py/releases/tag/orm-tornado) tag.