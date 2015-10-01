#!/usr/bin/env python


class BaseVimeoException(Exception):

    def __init__(self, request, message):

        json = None
        try:
            json = request.json()
        except:
            pass
            
        if json:
            message = json['error']
        else:
            message = request.text

        # API error message
        self.message = message

        # HTTP status code
        self.status_code = request.status_code

        super(BaseVimeoException, self).__init__(self.message)


class ObjectLoadFailure(Exception):

    def __init__(self, message):
        super(ObjectLoadFailure, self).__init__(message)


class UploadTicketCreationFailure(BaseVimeoException):

    def __init__(self, request, message):
        super(UploadTicketCreationFailure, self).__init__(request, message)


class VideoCreationFailure(BaseVimeoException): 

    def __init__(self, request, message):
        super(VideoCreationFailure, self).__init__(request, message)


class VideoUploadFailure(BaseVimeoException): 

    def __init__(self, request, message):
        super(VideoUploadFailure, self).__init__(request, message)


class PictureCreationFailure(BaseVimeoException): 

    def __init__(self, request, message):
        super(PictureCreationFailure, self).__init__(request, message)


class PictureUploadFailure(BaseVimeoException): 

    def __init__(self, request, message):
        super(PictureUploadFailure, self).__init__(request, message)


class PictureActivationFailure(BaseVimeoException): 

    def __init__(self, request, message):
        super(PictureActivationFailure, self).__init__(request, message)


class TexttrackCreationFailure(BaseVimeoException):

    def __init__(self, request, message):
        super(TexttrackCreationFailure, self).__init__(request, message)


class TexttrackUploadFailure(BaseVimeoException):

    def __init__(self, request, message):
        super(TexttrackUploadFailure, self).__init__(request, message)
