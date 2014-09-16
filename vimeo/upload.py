#! /usr/bin/env python
# encoding: utf-8

import os
import requests.exceptions

class UploadVideoMixin(object):
    """Handle uploading a new video to the Vimeo API."""

    UPLOAD_ENDPOINT = '/me/videos'

    def upload(self, filename):
        """Upload the named file to Vimeo."""
        ticket = self.post(self.UPLOAD_ENDPOINT, data={'type': 'streaming'})

        assert ticket.status_code == 201, "Failed to create an upload ticket"

        ticket = ticket.json()

        # Perform the actual upload.
        target = ticket['upload_link']
        size = os.path.getsize(filename)
        last_byte = 0
        with open(filename) as f:
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

        assert finalized_resp.status_code == 201, "Failed to create the video."

        return finalized_resp.headers.get('Location', None)

    def _get_progress(self, upload_target, filesize):
        """Test the completeness of the upload."""
        progress_response = self.put(
            upload_target,
            headers={'Content-Range': 'bytes */*'})

        range_recv = progress_response.headers.get('Range', None)
        _, last_byte = range_recv.split('-')

        return last_byte

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
            headers={
                'Content-Length': size,
                'Content-Range': 'bytes: %d-%d/%d' % (last_byte, size, size)
            }, data=f)

        assert response.status_code == 200, "Unexpected status code on upload."

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
            assert obj.status_code == 200, "Failed to load the target object."
            obj = obj.json()

        # Get the picture object.
        picture = self.post(obj['metadata']['connections']['pictures']['uri'])

        assert picture.status_code == 201, \
            "Failed to create a new picture with Vimeo."

        picture = picture.json()

        with open(filename) as f:
            upload_resp = self.put(picture['link'], data=f)
        assert upload_resp.status_code == 200, "Failed uploading"

        if activate:
            active = self.patch(picture['uri'], data={"active": "true"})
            assert active.status_code == 200, "Failed activating"
            picture['active'] = True

        return picture

class UploadMixin(UploadVideoMixin, UploadPictureMixin):
    """Handle uploading to the Vimeo API."""
    pass
