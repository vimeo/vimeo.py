import sys
from unittest.mock import Mock

import pytest

from vimeo.upload import UploadTexttrackMixin, UploadVideoMixin


@pytest.mark.parametrize('path_form', ['native', 'forward_slashes', 'path'])
def test_texttrack_uses_filename_without_directory(tmp_path, path_form):
    if path_form == 'path' and sys.version_info < (3, 6):
        pytest.skip('PathLike support requires Python 3.6')
    subtitles = tmp_path / 'captions.vtt'
    subtitles.write_bytes(b'WEBVTT\n')
    filename = {
        'native': str(subtitles),
        'forward_slashes': subtitles.as_posix(),
        'path': subtitles,
    }[path_form]
    upload = UploadTexttrackMixin()
    result = {'link': 'https://example.com/upload', 'uri': '/texttracks/1'}
    upload.post = Mock(return_value=Mock(status_code=201))
    upload.post.return_value.json.return_value = result
    uploaded = []

    def put(url, data):
        assert url == result['link']
        uploaded.append(data.read())
        return Mock(status_code=200)

    upload.put = put
    actual = upload.upload_texttrack('/videos/1', 'subtitles', 'en', filename)
    assert actual == result
    assert upload.post.call_args[1]['data']['name'] == 'captions.vtt'
    assert uploaded == [b'WEBVTT\n']


def test_apply_chunk_size_rules():
    """
    Test ensures that the expected behavior for
    `UploadVideoMixin.apply_chunk_size_rules` follows the general rule, that
    any proposed `chunk_size` is fine as long as it does not result in more
    than 1024 `chunks`. This is important because as the number of `chunks`
    increases the likely hood of various TUS server errors increases as well.
    """

    # The following cases result in < 1024 and as such should be allowed
    assert UploadVideoMixin.apply_chunk_size_rules(1, 1024) == 1
    assert UploadVideoMixin.apply_chunk_size_rules(3, 1024) == 3

    # A `chunk_size` larger than `file_size` is ok
    assert UploadVideoMixin.apply_chunk_size_rules(3, 1) == 3
    assert UploadVideoMixin.apply_chunk_size_rules(1024, 1) == 1024

    # A `chunk_size` <= 0 is equivalent to 1 byte.
    assert UploadVideoMixin.apply_chunk_size_rules(0, 1024) == 1
    assert UploadVideoMixin.apply_chunk_size_rules(-1000, 1024) == 1

    # The following cases all result in > 1024 chunks.
    assert UploadVideoMixin.apply_chunk_size_rules(1, 1025) == 2

    # 20 MB chunks for a 100000 MB file (100GB)
    assert UploadVideoMixin.apply_chunk_size_rules(
        (20 * 1024 * 1024),
        (100000 * 1024 * 1024)
    ) == 102400001
