"""
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
"""
import logging as log
import json
from urllib import urlencode

from tornado.httpclient import HTTPClient, HTTPError


class Uploader():
    """
    Class responsible for uploading videos via the Vimeo API
    """
    def __init__(self, config):
        self.config = config
        self.standard_headers = {
            'Accept': config['accept'],
            'Authorization': 'bearer %s' % config['access_token'],
            'User-Agent': config['user-agent']
        }
        self.ticket_path = "/me/videos"

    def __call__(self, name, post_check_hook=None):
        """
        Perform an upload of the given file to the current user's account

        The upload process consists of three steps and a loop.
        First, we request and receive an "upload ticket" from Vimeo. This ticket
        represents our place in the queue of videos waiting to upload.
        After successfully obtaining this ticket, we upload the binary data of the
        video. To do this, we make an HTTP request whose body contains some
        amount of the video's binary data. In response to a subsequent request, Vimeo tells us how
        much of the binary data was successfully uploaded. We repeat this process
        until Vimeo tells us the entirety of the file has been uploaded successfully.
        Once the entire video has been uploaded, the last step is to delete the
        upload ticket with another HTTP request. This action finalizes the upload
        process.

        Args:
        name (String)   -- The relative filepath of the file to upload

        Kwargs:
        post_check_hook (Function)  -- Function to call after each upload check
        """
        def do_upload():
            video_data, filetype = self.read_file(name)

            ticket_id, upload_uri, complete_uri = self.get_upload_ticket()
            log.info("Ticket ID: %s" % ticket_id)

            _range = 0
            hook_break = False
            while _range < len(video_data) and hook_break != True:
                self.upload_segment(upload_uri, _range, video_data, filetype or 'mp4')
                _range = self.get_last_uploaded_byte(upload_uri)
                # hook is passed the range, breaks retry cycle if it returns True
                if post_check_hook:
                    hook_break = post_check_hook(_range)

            log.info("Upload completed")
            return self.delete_upload_ticket(complete_uri)

        return do_upload()

    def read_file(self, filename):
        """
        Open a binary file and return its contents and extension

        Args:
        filename (String)   -- The relative path of the file to read
        """
        data = None
        with open(filename, "rb") as f:
            data = f.read()
        filetype = filename.split('.')[-1] if '.' in filename.split('/')[-1] else None
        return data, filetype

    def get_upload_ticket(self):
        """
        Obtain an upload ticket from the API

        Makes a POST request with type: streaming that registers and returns
        an upload ticket

        Returns the ticket identifier, upload uri, and upload completion uri

        Return: tuple of ticket_id, upload_uri, complete_uri
        """
        r = HTTPClient().fetch(self.config['apiroot'] + self.ticket_path, method="POST",
                body=urlencode({'type': 'streaming'}), headers = self.standard_headers,
                validate_cert=not self.config['dev'])
        response = json.loads(r.body)
        return response['ticket_id'], response['upload_link_secure'], response['complete_uri']

    def upload_segment(self, upload_uri, _range, data, filetype):
        """
        Upload a piece of a video file to Vimeo
        Makes a PUT request to the given URL with the given binary data

        The _range parameter indicates the first byte to send. The first time you
        attempt an upload, this will be 0. The next time, it will be the number
        returned from get_last_uploaded_byte, if that number is less than the total
        size of the video file in bytes.

        Args:
        upload_uri (String)     -- The url to request when uploading
        _range (Number)         -- The byte index in the file to start from
        data (Binary String)    -- The binary data of the video
        """
        content_range = '%d-%d/%d' % (_range, len(data), len(data))
        upload_headers = {'Content-Type': 'video/%s' % filetype,
                        'Content-Length': len(data),
                        'Content-Range': 'bytes: %s' % content_range}

        log.info("Sending file of size %d" % len(data))
        log.info("Requesting %s" % upload_uri)
        request_headers = dict(upload_headers.items() + self.standard_headers.items())
        r = HTTPClient().fetch(upload_uri, method="PUT",
                               body=data, headers=request_headers)
        log.info("Uploaded segment: status code %d" % r.code)
        if r.code != 200:
            raise ValueError("Upload unsuccessful")

    def get_last_uploaded_byte(self, check_uri):
        """
        Get the last byte index of the file successfully uploaded

        Performs a PUT to the given url, which returns a Range header
        indicating how much of the video file was successfully uploaded.
        If less than the total file size, this number is used in subsequent calls to
        upload_segment

        Args:
        check_uri (String)  -- The URI to which to perform the PUT request
        """
        upload_check_headers = {'Content-Range': 'bytes */*'}
        request_headers = dict(upload_check_headers.items() + self.standard_headers.items())
        try:
            HTTPClient().fetch(check_uri, method="PUT", body='', headers=request_headers)
        except HTTPError as e:
            log.info("Upload check: status code %s" % e.code)
            if e.code == 308:
                _range = int(e.response.headers['Range'].split('-')[1])
                log.info("Last uploaded byte: %d" % _range)
                return _range
            else: raise
        raise ValueError("Upload check unsuccessful")

    def delete_upload_ticket(self, complete_uri):
        """
        Delete the upload ticket (to be used once
        get_last_uploaded_byte() == total file size)

        Makes a DELETE request to the given URI, removing the upload ticket and
        setting the upload status to "processing"

        Args:
        complete_uri (String)   -- The URI to which to make the DELETE request

        Return: The ID of the newly uploaded video
        """
        url = self.config['apiroot'] + complete_uri
        log.info("Requesting %s" % url)
        r = HTTPClient().fetch(url, method="DELETE", headers=self.standard_headers,
                               validate_cert=not self.config['dev'])
        log.info("Upload completed: status code: %d" % r.code)
        if r.code == 201:
            _id = r.headers['location'].split('/')[-1]
            return _id
        raise ValueError("Upload completion unsuccessful")
