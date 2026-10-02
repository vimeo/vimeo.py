import requests

from vimeo import VimeoClient


def test_token_before_authentication():
    client = VimeoClient(key='key', secret='secret')
    assert client.token is None


def test_token_can_be_cleared_and_replaced():
    client = VimeoClient(token='initial')
    assert client.token == 'initial'

    client.token = None
    assert client.token is None

    client.token = 'replacement'
    assert client.token == 'replacement'
    request = requests.Request(
        'GET', 'https://example.com', auth=client._token)
    assert request.prepare().headers['Authorization'] == 'Bearer replacement'
