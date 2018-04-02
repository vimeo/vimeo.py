#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

import os
import io
import requests.exceptions
from tusclient import client
from . import exceptions

try:
    basestring
except NameError:
    basestring = str


class UploadVideoMixin(object):
    """Handle uploading a new video to the Vimeo API."""

    UPLOAD_ENDPOINT = '/me/videos'
    VERSIONS_ENDPOINT = '{video_uri}/versions'

    def upload(self, filename, **kwargs):
        """Upload a file.

        This should be used to upload a local file. If you want a form for your
        site to upload direct to Vimeo, you should look at the `POST
        /me/videos` endpoint.

        https://developer.vimeo.com/api/endpoints/videos#POST/users/{user_id}/videos

        Args:
            filename (string): Path on disk to file
            **kwargs: Supply a `data` dictionary for data to set to your video
                when uploading. See the API documentation for parameters you
                can send. This is optional.

        Returns:
            string: The Vimeo Video URI of your uploaded video.

        Raises:
            UploadAttemptCreationFailure: If we were unable to create an upload
                attempt for you.
            VideoUploadFailure: If unknown errors occured when uploading your
                video.
        """

        filesize = self.__get_file_size(filename)
        uri = self.UPLOAD_ENDPOINT
        data = kwargs['data'] if 'data' in kwargs else {}

        # Ignore any specified upload approach and size.
        if 'upload' not in data:
            data['upload'] = {
                'approach': 'tus',
                'size': filesize
            }
        else:
            data['upload']['approach'] = 'tus'
            data['upload']['size'] = filesize

        attempt = self.post(uri, data=data, params={'fields': 'uri,upload'})
        if attempt.status_code != 200:
            raise exceptions.UploadAttemptCreationFailure(
                attempt,
                "Unable to initiate an upload attempt."
            )

        attempt = attempt.json()

        return self.__perform_tus_upload(filename, attempt)

    def replace(self, video_uri, filename, **kwargs):
        """Replace the source of a single Vimeo video.

        https://developer.vimeo.com/api/endpoints/videos#POST/videos/{video_id}/versions

        Args:
            video_uri (string): Vimeo Video URI
            filename (string): Path on disk to file
            **kwargs: Supply a `data` dictionary for data to set to your video
                when uploading. See the API documentation for parameters you
                can send. This is optional.

        Returns:
            string: The Vimeo Video URI of your replaced video.
        """
        filesize = self.__get_file_size(filename)
        uri = self.VERSIONS_ENDPOINT.format(video_uri=video_uri)

        data = kwargs['data'] if 'data' in kwargs else {}
        data['file_name'] = os.path.basename(filename)

        # Ignore any specified upload approach and size.
        if 'upload' not in data:
            data['upload'] = {
                'approach': 'tus',
                'size': filesize
            }
        else:
            data['upload']['approach'] = 'tus'
            data['upload']['size'] = filesize

        attempt = self.post(uri, data=data, params={'fields': 'upload'})
        if attempt.status_code != 201:
            raise exceptions.UploadAttemptCreationFailure(
                attempt,
                "Unable to initiate an upload attempt."
            )

        attempt = attempt.json()

        # `uri` doesn't come back from `/videos/:id/versions` so we need to
        # manually set it here for uploading.
        attempt['uri'] = video_uri

        return self.__perform_tus_upload(filename, attempt)

    def __perform_tus_upload(self, filename, attempt):
        """Take an upload attempt and perform the actual upload via tus.

        https://tus.io/

        Args:
            attempt (:obj): requests object
            path (string): path on disk to file
            filename (string): name of the video file on vimeo.com

        Returns:
            string: The Vimeo Video URI of your uploaded video.

        Raises:
            VideoUploadFailure: If unknown errors occured when uploading your
                video.
        """
        upload_link = attempt.get('upload').get('upload_link')

        try:
            with io.open(filename, 'rb') as fs:
                tus_client = client.TusClient('https://files.tus.vimeo.com')
                uploader = tus_client.uploader(file_stream=fs, url=upload_link)
                uploader.upload()
        except Exception as e:
            raise exceptions.VideoUploadFailure(
                e,
                'Unexpected error when uploading through tus.'
            )

        return attempt.get('uri')

    def __get_file_size(self, filename):
        """Get the size of a specific file.

        Args:
            filename (string): Path on disk to file

        Returns:
            integer: The size of the file.
        """

        try:
            return os.path.getsize(filename)
        except TypeError:
            return len(filename.read())


class UploadPictureMixin(object):
    """
    Class for uploading a picture to Vimeo.

    Functionality for uploading a picture to Vimeo for another object
    (video, user, etc).
    """

    BASE_FIELDS = set(('link', 'uri'))

    def upload_picture(self, obj, filename, activate=False, fields=None):
        """
        Upload a picture for the object.

        The object (obj) can be the URI for the object or the response/parsed
        json for it.
        """
        if isinstance(obj, basestring):
            obj = self.get(
                obj, params={'fields': 'metadata.connections.pictures.uri'})

            if obj.status_code != 200:
                raise exceptions.ObjectLoadFailure(
                    "Failed to load the target object")
            obj = obj.json()

        if isinstance(fields, basestring):
            fields = set((field.strip() for field in fields.split(',')))

        fields = self.BASE_FIELDS.union(fields) if fields else self.BASE_FIELDS

        # Get the picture object.
        picture = self.post(
            obj['metadata']['connections']['pictures']['uri'],
            params={'fields': ','.join(fields)}
        )

        if picture.status_code != 201:
            raise exceptions.PictureCreationFailure(
                picture, "Failed to create a new picture with Vimeo.")

        picture = picture.json()

        with io.open(filename, 'rb') as f:
            upload_resp = self.put(
                picture['link'],
                data=f,
                params={'fields': 'error'})
        if upload_resp.status_code != 200:
            raise exceptions.PictureUploadFailure(
                upload_resp, "Failed uploading picture")

        if activate:
            active = self.patch(
                picture['uri'],
                data={"active": "true"},
                params={'fields': 'error'})
            if active.status_code != 200:
                raise exceptions.PictureActivationFailure(
                    active, "Failed activating picture")
            picture['active'] = True

        return picture


class UploadTexttrackMixin(object):
    """Functionality for uploading a texttrack to Vimeo for a video."""

    TEXTTRACK_ENDPOINT = '{video_uri}/texttracks'
    BASE_FIELDS = set(('link',))

    def upload_texttrack(self, video_uri, track_type, language, filename,
                         fields=None):
        """Upload the texttrack at the given uri with the named source file."""
        uri = self.TEXTTRACK_ENDPOINT.format(video_uri=video_uri)
        name = filename.split('/')[-1]

        if isinstance(fields, basestring):
            fields = set((field.strip() for field in fields.split(',')))

        fields = self.BASE_FIELDS.union(fields) if fields else self.BASE_FIELDS

        texttrack = self.post(uri,
                              data={'type': track_type,
                                    'language': language,
                                    'name': name},
                              params={'fields': ','.join(fields)})

        if texttrack.status_code != 201:
            raise exceptions.TexttrackCreationFailure(
                texttrack, "Failed to create a new texttrack with Vimeo")

        texttrack = texttrack.json()

        with io.open(filename, 'rb') as f:
            upload_resp = self.put(texttrack['link'], data=f)
        if upload_resp.status_code != 200:
            raise exceptions.TexttrackUploadFailure(
                upload_resp, "Failed uploading texttrack")

        return texttrack


class UploadMixin(UploadVideoMixin, UploadPictureMixin, UploadTexttrackMixin):
    """Handle uploading to the Vimeo API."""

    pass
