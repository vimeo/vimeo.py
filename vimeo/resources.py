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
from vimeoresource import VimeoResource, CallableVimeoResource, SingularResource


"""
This file consists of subclass declarations for VimeoResource.
The most important attribute of each class is set via the merge_properties()
method. These dictionaries are used to determine what subresources each
resource can access, which methods are allowed on each, what content type to
accept, and more.

See the docstring in vimeoresource.SingularResource.__init__ for a detailed
description of what each key in the properties dictionary means.
"""


class Users(CallableVimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Users, self).__init__(config, urlpath, properties)
        self._cat_url_path("/users")
        self._singular = User
        self.accept = 'person'


class User(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(User, self).__init__(name, path, config, properties)
        self.accept = 'person'
        self.merge_properties({
            'activities' : {'methods': ["GET"]},
            'albums'     : {'methods': ["GET"],
                            'accept': 'album'},
            'appearances': {'methods': ["GET"]},
            'channels'   : {'methods': ["GET", "PUT", "DELETE"],
                            'accept': 'channel'},
            'groups'     : {'methods': ["GET", "PUT", "DELETE"],
                            'accept': 'group',
                            'search': False},
            'feed'       : {'methods': ["GET"]},
            'followers'  : {'methods': ["GET"],
                            'search': False,
                            'accept': 'user'},
            'following'  : {'methods': ["GET", "PUT", "DELETE"],
                            'accept': 'user',
                            'search': False},
            'likes'      : {'methods': ["GET", "PUT", "DELETE"],
                            'search': False,
                            'accept': 'video'},
            'portfolios' : {'methods': ["GET"],
                            'accept': 'portfolio',
                            'subresources': {
                                'videos': {
                                    'methods': ['GET'],
                                    'resource': True}
                                }},
            'presets'    : {'methods': ["GET"],
                            'single_get': True,
                            'accept': 'presets'},
            'videos'     : {'methods': ["GET", "POST"],
                            'accept': 'video'},
            'watchlater' : {'methods': ["GET", "PUT", "DELETE"],
                            'accept': 'video',
                            'multi_put': True,
                            'search': False}  # off due to a 500 error
        })


class Albums(VimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Albums, self).__init__(config, urlpath, properties)
        self._cat_url_path("/albums")
        self._singular = Album
        self.accept = 'album'


class Album(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(Album, self).__init__(name, path, config, properties)
        self.accept = 'album'
        self.merge_properties({
            'videos': {'methods': ["GET", "PUT", "DELETE"],
                       'accept': 'video',
                       'search': False}  # off due to a 500 error
        })


class Categories(CallableVimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Categories, self).__init__(config, urlpath, properties)
        self._cat_url_path("/categories")
        self._singular = Category


class Category(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(Category, self).__init__(name, path, config, properties)
        self.merge_properties({
            'channels': {'methods': ["GET"],
                         'accept': 'channel'},
            'groups'  : {'methods': ["GET"],
                         'accept': 'group'},
            'tags'    : {'methods': ["GET"]},
            'users'   : {'methods': ["GET"],
                         'accept': 'user'},
            'videos'  : {'methods': ["GET"],
                         'accept': 'video'}
        })


class Channels(CallableVimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Channels, self).__init__(config, urlpath, properties)
        self._cat_url_path("/channels")
        self._singular = Channel
        self.accept = 'channel'


class Channel(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(Channel, self).__init__(name, path, config, properties)
        self.accept = 'channel'
        self.methods = ["GET", "PATCH", "DELETE"]
        self.merge_properties({
            'users' : {'methods': ["GET"],
                       'accept': 'user',
                       'filter': False,
                       'search': False},
            'videos': {'methods': ["GET", "PUT", "DELETE"],
                       'accept': 'video',
                       'search': False}  # off due to a 500 error
        })


class Groups(CallableVimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Groups, self).__init__(config, urlpath, properties)
        self._cat_url_path("/groups")
        self._singular = Group
        self.accept = 'group'


class Group(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(Group, self).__init__(name, path, config, properties)
        self.accept = 'group'
        self.methods = ["GET", "PATCH", "DELETE"]
        self.merge_properties({
            'users' : {'methods': ["GET"],
                       'accept': 'user'},
            'videos': {'methods': ["GET", "PUT", "DELETE"],
                       'accept': 'video'}
        })


class Portfolios(CallableVimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Portfolios, self).__init__(config, urlpath, properties)
        self._cat_url_path("/portfolios")
        self._singular = Portfolio
        self.accept = 'portfolio'


class Portfolio(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(Portfolio, self).__init__(name, path, config, properties)
        self.accept = 'portfolio'
        self.merge_properties({
            'videos': {'methods': ["GET", "PUT", "DELETE"],
                       'accept': 'video'}
        })


class Videos(CallableVimeoResource):
    def __init__(self, config, urlpath="", properties={}):
        super(Videos, self).__init__(config, urlpath, properties)
        self._cat_url_path("/videos")
        self._singular = Video
        self.accept = 'video'


class Video(SingularResource):
    def __init__(self, name, path, config, properties={}):
        super(Video, self).__init__(name, path, config, properties)
        self.accept = 'video'
        self.methods = ["GET", "PATCH", "DELETE"]
        self.merge_properties({
                'comments': {'methods': ["GET", "POST", "PATCH", "DELETE"],
                             'accept': 'comment'},
                'credits' : {'methods': ["GET", "POST", "DELETE"],
                            'accept': 'credit'},
                'likes'   : {'methods': ["GET"]},
                'presets' : {'methods': ["GET", "PUT", "DELETE"]},
                'tags'    : {'methods': ["GET", "PUT", "DELETE"],
                             'accept': 'tag',
                             'multi_put': True},
                'stats'   : {'methods': ["GET"],
                             'accept': 'stats'},
        })

mapper = {
    "users": Users,
    "videos": Videos,
    "albums": Albums,
    "channels": Channels,
    "groups": Groups,
    "portfolios": Portfolios,
    "categories": Categories,
}
