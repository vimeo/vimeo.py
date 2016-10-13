#!/usr/bin/env python


class BaseVimeoException(Exception):
    def _get_message(self, response):
        json = None
        try:
            json = response.json()
        except:
            pass

        if json:
            message = json.get('error') or json.get('Description')
        else:
            message = response.text
        return message

    def __init__(self, response, message):
        # API error message
        self.message = self._get_message(response)

        # HTTP status code
        self.status_code = response.status_code

        super(BaseVimeoException, self).__init__(self.message)


class ObjectLoadFailure(Exception):

    def __init__(self, message):
        super(ObjectLoadFailure, self).__init__(message)


class UploadTicketCreationFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(UploadTicketCreationFailure, self).__init__(response, message)


class VideoCreationFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(VideoCreationFailure, self).__init__(response, message)


class VideoUploadFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(VideoUploadFailure, self).__init__(response, message)


class PictureCreationFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(PictureCreationFailure, self).__init__(response, message)


class PictureUploadFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(PictureUploadFailure, self).__init__(response, message)


class PictureActivationFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(PictureActivationFailure, self).__init__(response, message)


class TexttrackCreationFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(TexttrackCreationFailure, self).__init__(response, message)


class TexttrackUploadFailure(BaseVimeoException):

    def __init__(self, response, message):
        super(TexttrackUploadFailure, self).__init__(response, message)


class APIRateLimitExceededFailure(BaseVimeoException):

    def _get_message(self, response):
        guidelines = 'https://developer.vimeo.com/guidelines/rate-limiting'
        message = super(APIRateLimitExceededFailure, self)._get_message(
            response
        )
        limit_reset_time = response.headers.get('x-ratelimit-reset')
        if limit_reset_time:
            text = '{} \n limit will reset on: {}.\n About this limit: {}'
            message = text.format(
                message,
                limit_reset_time,
                guidelines
            )
        return message
