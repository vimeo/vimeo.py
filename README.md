# PyVimeo

This is a simple library for interacting with the [Vimeo API](https://developers.vimeo.com).

### Example Usage

```python
import vimeo

v = vimeo.VimeoClient(
    token=YOUR_AUTHENTICATED_BEARER_TOKEN,
    key=YOUR_API_TOKEN,
    secret=YOUR_TOKEN_SECRET)

# Make the request to the server for the "/me" endpoint.
about_me = v.get('/me')

assert about_me.status_code == 200  # Make sure we got back a successful response.
print about_me.json()   # Load the body's JSON data.

```

Note:  You can find the app tokens and an authenticated bearer token in the "OAuth 2" tab for your app on the [Vimeo developer site](https://developer.vimeo.com/apps).

### Authenticating

There are two main types of authentication in the Vimeo API:
0. Client Credentials: A token that is specific to your app and NOT a user.
0. Authorization Code: A token that is for your app, but has the ability to act on behalf of the authorizing user.

Note:  Both types of authentication require you go to the [Vimeo developer site](https://developer.vimeo.com/apps) and register an application with Vimeo.

#### Client Credentials

Retrieving a set of client credentials in this library is very, very easy.  You must provide the `VimeoClient` with the `key` and `secret` for your app, and make a single call.  The example below contains all the necessary steps.  At the end of it, the `VimeoClient` instance (the variable `v`) will be authenticated with the token, and you can store the value - returned by the `load_client_credentials()` call - in your database or a file to use like the example at the start of this README.

```python
v = vimeo.VimeoClient(
    key=YOUR_API_TOKEN,
    secret=YOUR_TOKEN_SECRET)
token = v.load_client_credentials()
```

#### Authorization Code

Getting a bearer token via the authorization code method is a bit more complicated.  The most important thing to understand is that we need to go through a series of basic steps:

0. We send the user to a web page where they can choose to accept or reject the permissions we are asking for.
0. When the user makes their selection and accepts or rejects your app, the user is redirected to a webpage specified by you.
0. If the user authorized your app, you can exchange the code provided for the bearer token.

This can be done with this library using some basic helper functions.  The code below demonstrates, but do note that there are 2 sections, where you redirect the user to Vimeo, and where the user returns so you can perform the final step.

```python
"""This section is used to determine where to direct the user."""
v = vimeo.VimeoClient(
    key=YOUR_API_TOKEN,
    secret=YOUR_TOKEN_SECRET)

vimeo_authorization_url = v.auth_url(['public', 'private'], 'https://example.com')

# Your application should now redirect to vimeo_authorization_url.
```

```python
"""This section completes the authentication for the user."""
v = vimeo.VimeoClient(
    key=YOUR_API_TOKEN,
    secret=YOUR_TOKEN_SECRET)

# You should retrieve the "code" from the URL string Vimeo redirected to.  Here that's named CODE_FROM_URL
token, user, scope = v.exchange_code(CODE_FROM_URL, 'https://example.com')

# Store the token, scope and any additional user data you require in your database so users do not have to re-authorize your application repeatedly.
```

This process is generally quite simple, but it does require a little more effort than the client credentials grant to make work properly.  Remember that you may ask for scopes that the user decides *not* to give you, and your application must gracefully handle that.

### Uploading a new video

Once you have an authenticated instance of the `VimeoClient` class, uploading is a single function call away.  Internally, this library will provide the `streaming` upload and send a local file to the server.

```python
v = vimeo.VimeoClient(
    key=YOUR_API_TOKEN,
    secret=YOUR_TOKEN_SECRET)

v.upload('your-filename.mp4')
```
