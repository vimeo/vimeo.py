from unittest import TestCase
from unittest.mock import Mock, patch

from vimeo import VimeoClient


class ClientHeadersTest(TestCase):
    @patch('vimeo.client.requests.post')
    def test_json_request_does_not_mutate_caller_headers(self, post):
        post.return_value = Mock(status_code=200)
        headers = {'X-Custom': 'retained', 'Content-Type': 'text/plain'}
        original = headers.copy()

        VimeoClient(token='token').post('/me/videos', data={}, headers=headers)

        self.assertEqual(headers, original)
        sent = post.call_args[1]['headers']
        self.assertEqual(sent['Content-Type'], 'application/json')
        self.assertEqual(sent['Accept'], VimeoClient.ACCEPT_HEADER)
        self.assertEqual(sent['User-Agent'], VimeoClient.USER_AGENT)
        self.assertEqual(sent['X-Custom'], 'retained')

    @patch('vimeo.client.requests.get')
    def test_none_headers_uses_defaults(self, get):
        get.return_value = Mock(status_code=200)

        VimeoClient(token='token').get('/me', headers=None)

        self.assertEqual(get.call_args[1]['headers'], {
            'Accept': VimeoClient.ACCEPT_HEADER,
            'User-Agent': VimeoClient.USER_AGENT,
        })
