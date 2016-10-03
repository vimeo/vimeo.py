#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

import os
import io
import requests.exceptions
from .exceptions import *

try:
    basestring
except NameError:
    basestring = str

class UploadVideoMixin(object):
    """Handle uploading a new video to the Vimeo API."""

    UPLOAD_ENDPOINT = '/me/videos'
    REPLACE_ENDPOINT = '{video_uri}/files'

    def upload(self, filename, upgrade_to_1080=False):
        """Upload the named file to Vimeo."""
        ticket = self.post(self.UPLOAD_ENDPOINT,
                data={'type': 'streaming',
                      'upgrade_to_1080': 'true' if upgrade_to_1080 else 'false'})

        return self._perform_upload(filename, ticket)

    def replace(self, video_uri, filename, upgrade_to_1080=False):
        """Replace the video at the given uri with the named source file."""
        uri = self.REPLACE_ENDPOINT.format(video_uri=video_uri)

        ticket = self.put(uri,
            data={'type': 'streaming',
                  'upgrade_to_1080': 'true' if upgrade_to_1080 else 'false'})

        return self._perform_upload(filename, ticket)

    def _perform_upload(self, filename, ticket):
        """Take an upload ticket and perform the actual upload."""

        if ticket.status_code != 201:
            raise UploadTicketCreationFailure(ticket, "Failed to create an upload ticket")

        ticket = ticket.json()

        # Perform the actual upload.
        target = ticket['upload_link']
        last_byte = 0
        # Try to get size of obj by path. If provided obj is not a file path
        # find the size of file-like object.
        try:
            size = os.path.getsize(filename)
            with io.open(filename, 'rb') as f:
                while last_byte < size:
                    try:
                        self._make_pass(target, f, size, last_byte)
                    except requests.exceptions.Timeout:
                        # If there is a timeout here, we are okay with it, since
                        # we'll check and resume.
                        pass
                    last_byte = self._get_progress(target, size)
        except TypeError:
            size = len(filename.read())
            f = filename
            while last_byte < size:
                try:
                    self._make_pass(target, f, size, last_byte)
                except requests.exceptions.Timeout:
                    # If there is a timeout here, we are okay with it, since
                    # we'll check and resume.
                    pass
                last_byte = self._get_progress(target, size)

        # Perform the finalization and get the location.
        finalized_resp = self.delete(ticket['complete_uri'])

        if finalized_resp.status_code != 201:
            raise VideoCreationFailure(finalized_resp, "Failed to create the video")

        return finalized_resp.headers.get('Location', None)

    def _get_progress(self, upload_target, filesize):
        """Test the completeness of the upload."""
        progress_response = self.put(
            upload_target,
            headers={'Content-Range': 'bytes */*'})

        range_recv = progress_response.headers.get('Range', None)
        _, last_byte = range_recv.split('-')

        return int(last_byte)

    def _make_pass(self, upload_target, f, size, last_byte):
        """Make a pass at uploading.

        This particular function may do many things.  If this is a large upload
        it may terminate without having completed the upload.  This can also
        occur if there are network issues or any other interruptions.  These
        can be recovered from by checking with the server to see how much it
        has and resuming the connection.
        """
        response = self.put(
            upload_target,
            timeout=None,
            headers={
                'Content-Length': str(size),
                'Content-Range': 'bytes: %d-%d/%d' % (last_byte, size, size)
            }, data=f)

        if response.status_code != 200:
            raise VideoUploadFailure(response, "Unexpected status code on upload")


class UploadPictureMixin(object):
    """Functionality for uploading a picture to Vimeo for another object
    (video, user, etc).
    """

    def upload_picture(self, obj, filename, activate=False):
        """Upload a picture for the object.

        The object (obj) can be the URI for the object or the response/parsed
        json for it.
        """
        if isinstance(obj, basestring):
            # TODO:  Add filtering down to just the picture connection field.
            obj = self.get(obj)

            if obj.status_code != 200:
                raise ObjectLoadFailure("Failed to load the target object")
            obj = obj.json()

        # Get the picture object.
        picture = self.post(obj['metadata']['connections']['pictures']['uri'])

        if picture.status_code != 201:
            raise PictureCreationFailure(picture, "Failed to create a new picture with Vimeo.")

        picture = picture.json()

        with io.open(filename, 'rb') as f:
            upload_resp = self.put(picture['link'], data=f)
        if upload_resp.status_code != 200:
            raise PictureUploadFailure(upload_resp, "Failed uploading picture")

        if activate:
            active = self.patch(picture['uri'], data={"active": "true"})
            if active.status_code != 200:
                raise PictureActivationFailure(active, "Failed activating picture")
            picture['active'] = True

        return picture

class UploadTexttrackMixin(object):
    """Functionality for uploading a texttrack to Vimeo for a video.
    """
    TEXTTRACK_ENDPOINT = '{video_uri}/texttracks'

    def upload_texttrack(self, video_uri, track_type, language, filename):
        """Upload the texttrack at the given uri with the named source file."""
        uri = self.TEXTTRACK_ENDPOINT.format(video_uri=video_uri)
        name = filename.split('/')[-1]

        texttrack = self.post(uri,
                              data={'type': track_type,
                                    'language': language,
                                    'name': name})

        if texttrack.status_code != 201:
            raise TexttrackCreationFailure(texttrack, "Failed to create a new texttrack with Vimeo")

        texttrack = texttrack.json()

        with io.open(filename, 'rb') as f:
            upload_resp = self.put(texttrack['link'], data=f)
        if upload_resp.status_code != 200:
            raise TexttrackUploadFailure(upload_resp, "Failed uploading texttrack")

        return texttrack


class UploadMixin(UploadVideoMixin, UploadPictureMixin, UploadTexttrackMixin):
    """Handle uploading to the Vimeo API."""
    pass
