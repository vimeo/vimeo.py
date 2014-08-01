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
import pytest
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from vimeo import VimeoClient


vimeo = None

data = {
    'user': '20652831',
    'access_token': 'YOUR ACCESS TOKEN HERE',
    'client_id': 'YOUR CLIENT ID HERE',
    'client_secret': 'YOUR CLIENT SECRET HERE',
    'channel': 'c638518',
    'group': 'g211471',
    'presets': '325649',
    'likevideo': '76115773',
    'followuser': '12596222',
    'editvideo': 'v73879996',
    'portfolio': 'p166225',
    'album': 'a2639089',
    'category': "comedy",
    'uploadvideo': 'testupload.mp4'
}

@pytest.fixture
def setup():
    global vimeo
    vimeo = VimeoClient(data['access_token'])


class VimeoObjectTest():
    def search(self, resource, query='e'):
        r = getattr(vimeo, resource)(query=query)
        helpstring = "%s search" % (str(resource))
        if query:
            helpstring += " with a query"
        helpstring += " should return some resources"
        assert r['body']['total'] > 0, helpstring

        with pytest.raises(Exception):
            r = getattr(vimeo, resource)(_filter="test", msg="%s search should fail without query params")

        r = getattr(vimeo, resource)(query="test", _filter="test")
        assert r['body']['total'] > 0, "%s search should be filterable"

    def single_lookup(self, resource, identifier):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)
        r = resource()
        assert r['body']['name'], "Single %s lookup should return a resource" % (str(resource))

        r = resource(_filter='test')
        assert r['body']['name'], "Single %s lookup with filter should return a resource" % (str(resource))

        r = resource(content_filter='safe')
        assert r['body']['name'], "Single %s lookup with content filter should return a resource" % (str(resource))

        def handle(response, error):
            assert response['body']['name'], "Single %s lookup should work asynchronously" % (str(resource))
        resource(_callback=handle)

    def multi_lookup(self, resource, identifier, endpoint):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)
        r = getattr(resource, endpoint)()
        assert r['body'], "%s %s lookup should return an object" % (str(resource), endpoint)
        assert 'data' in r['body'], "%s %s lookup should return some data" % (str(resource), endpoint)

        r = getattr(resource, endpoint)(query='test')
        assert r['body'], "%s %s lookup with search should return an object" % (str(resource), endpoint)
        assert 'data' in r['body'], "%s %s lookup with search should return some data" % (str(resource), endpoint)

        r = getattr(resource, endpoint)(_filter='test')
        assert r['body'], "%s %s lookup with filter should return an object" % (str(resource), endpoint)
        assert 'data' in r['body'], "%s %s lookup with filter should return some data" % (str(resource), endpoint)

        r = getattr(resource, endpoint)(content_filter='safe')
        assert r['body'], "%s %s lookup with content filter should return an object" % (str(resource), endpoint)
        assert 'data' in r['body'], "%s %s lookup with content filter should return some data" % (str(resource), endpoint)

        r = getattr(resource, endpoint)(sort='date')
        assert r['body'], "%s %s lookup with sort should return an object" % (str(resource), endpoint)
        assert 'data' in r['body'], "%s %s lookup with sort should return some data" % (str(resource), endpoint)

        def handle(response, error):
            assert 'data' in response['body'], "%s %s lookup should work asynchronously" % (str(resource), endpoint)
        getattr(resource, endpoint)(_callback=handle)

    def put_item(self, resource, identifier, endpoint, put_id, check_get=True):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)

        getattr(resource, endpoint).put(put_id)
        mess = "%s should be able to add %s" % (str(resource), endpoint)
        if check_get:
            r = getattr(resource, endpoint)()
            match = [a for a in r['body']['data'] if put_id in a['uri']]
            assert len(match) == 1, mess
        else:
            assert True, mess + " (no exception should be thrown)"

    def exists(self, resource, identifier, endpoint, put_id):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)

        getattr(resource, endpoint).get(put_id)
        assert True, "%s GET should show exising %s" % (str(resource), endpoint)

    def get_item(self, resource, identifier, endpoint, put_id):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)

        r = getattr(resource, endpoint).get(put_id)
        assert put_id in r['body']['uri'], "%s should be able to get %s" % (str(resource), endpoint)

    def post_item(self, resource, identifier, endpoint, data, key_field='text'):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)

        getattr(resource, endpoint).post(data)
        r = getattr(resource, endpoint)()
        added_id = None
        for item in r['body']['data']:
            if data[key_field] == item[key_field]:
                added_id = item['uri']
                break
        assert added_id, "%s %s should be able to post a %s" % (str(resource), identifier, endpoint)
        return added_id

    def patch_item(self, resource, identifier, endpoint='', put_id=None, data={},
                   response_field='', key_field='text'):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)

        if len(data.keys()) == 1:
            key_field = data.keys()[0]

        user = False
        if not response_field:
            response_field = key_field
        elif response_field == 'user':
            user = True
            response_field = 'uri'

        if endpoint:
            getattr(resource, endpoint).patch(put_id, data)
            r = getattr(resource, endpoint)()
        else:
            resource.patch(data)
            r = resource()
        added_id = None
        if 'data' in r['body']:
            for item in r['body']['data']:
                if user:
                    if data[key_field] == item['user'][response_field].split('/')[-1]:
                        added_id = item['uri']
                        break
                else:
                    if data[key_field] == item[response_field]:
                        added_id = item['uri']
                        break
        else:
            if user:
                if r['body']['user'][response_field].split('/')[-1] == data[key_field]:
                    added_id = r['uri']
            else:
                if r['body'][response_field] == data[key_field]:
                    added_id = r['uri']
        assert added_id, "%s %s should be able to patch a %s" % (str(resource), identifier, endpoint)

    def delete_item(self, resource, identifier, endpoint, put_id, check_get=True):
        resources = getattr(vimeo, resource)
        resource = getattr(resources, identifier)

        getattr(resource, endpoint).delete(put_id)
        mess = "%s should be able to remove %s" % (str(resource), endpoint)
        if check_get:
            r = getattr(resource, endpoint)()
            match = [a for a in r['body']['data'] if put_id in a['uri']]
            assert len(match) == 0, mess
        else:
            assert True, mess + " (no exception should be thrown)"


@pytest.mark.usefixtures("setup")
class TestClient():
    def test_init(self):
        assert vimeo is not None, "VimeoClient should init successfully"
        assert vimeo.config['access_token'], "VimeoClient should have an access token"

    def test_unknown_attribute(self):
        with pytest.raises(Exception):
            vimeo.nothing()

    def test_nonexistent_file_upload(self):
        with pytest.raises(Exception):
            vimeo.upload("notafile.mp4")

    def test_auth_modes(self):
        vimeo = VimeoClient(access_token=data['access_token'])
        r = vimeo.me.videos()
        assert 'data' in r['body'], "Access token auth should work"

        vimeo = VimeoClient(client_id=data['client_id'], client_secret=data['client_secret'])
        r = vimeo.users.emmett9001()
        assert 'uri' in r['body'], "Basic auth with cid and secret should work"

        vimeo = VimeoClient(client_id=data['client_id'])
        r = vimeo.users.emmett9001()
        assert 'uri' in r['body'], "Basic auth with cid should work"

    def test_invalid_method(self):
        with pytest.raises(AttributeError):
            vimeo.me.followers.multiput(['literally', 'anything'])
        with pytest.raises(AttributeError):
            vimeo.me.followers.get('anything')


@pytest.mark.usefixtures("setup")
class TestUser(VimeoObjectTest):
    def test_users(self):
        self.search('users')

    def test_single_user(self):
        self.single_lookup('users', data['user'])

    def test_me(self):
        me = vimeo.me()
        user = getattr(vimeo.users, data['user'])()
        assert me['body']['uri'] == user['body']['uri'], "/me should return an identical uri"

    def test_user_activities(self):
        self.multi_lookup('users', data['user'], 'activities')

    def test_user_albums(self):
        self.multi_lookup('users', data['user'], 'albums')

    def test_user_appearances(self):
        self.multi_lookup('users', data['user'], 'appearances')

    def test_user_channels(self):
        self.multi_lookup('users', data['user'], 'channels')

        tchannel = data['channel'].strip("c")
        self.put_item('users', data['user'], 'channels', tchannel)
        self.delete_item('users', data['user'], 'channels', tchannel)

    def test_user_feed(self):
        self.multi_lookup('users', data['user'], 'feed')

    def test_user_followers(self):
        self.multi_lookup('users', data['user'], 'followers')

    def test_user_following(self):
        self.multi_lookup('users', data['user'], 'following')

        self.put_item('users', data['user'], 'following', data['followuser'])
        self.delete_item('users', data['user'], 'following', data['followuser'])

        with pytest.raises(Exception):
            vimeo.me.following.get(data['followuser'])

    def test_user_groups(self):
        self.multi_lookup('users', data['user'], 'groups')

        tgroup = data['group'].strip("g")
        self.put_item('users', data['user'], 'groups', tgroup)
        self.delete_item('users', data['user'], 'groups', tgroup)

    def test_user_likes(self):
        self.multi_lookup('users', data['user'], 'likes')

        self.put_item('users', data['user'], 'likes', data['likevideo'])
        self.delete_item('users', data['user'], 'likes', data['likevideo'])

    def test_user_portfolios(self):
        user = getattr(vimeo.users, data['user'])
        r = user.portfolios()
        assert r['body'], "User portfolio lookup should return an object"
        assert 'data' in r['body'], "User portfolio lookup should return some data"

        def handle(response, error):
            assert 'data' in response['body'], "User portfolio lookup should work asynchronously"
        user.portfolios(_callback=handle)

        r = user.portfolios.get(data['portfolio']).videos()
        assert r['body'], "User portfolio videos lookup should return an object"
        assert 'data' in r['body'], "User portfolio videos lookup should return some data"

        r = user.portfolios.get("test-portfolio")()
        assert True, "User portfolio should work with hyphen"

        pytest.skip(msg="User portfolios endpoint not found in prod")

        r = user.portfolios.get(data['portfolio']).videos.get("70429873")()
        assert r['body'], "User portfolio video lookup should return an object"
        assert 'uri' in r['body'], "User portfolio video lookup should return a video"

    def test_user_presets(self):
        self.multi_lookup('users', data['user'], 'presets')
        self.exists('users', data['user'], 'presets', data['presets'])

    def test_user_videos(self):
        self.multi_lookup('users', data['user'], 'videos')

        r = vimeo.me.videos.get(data['editvideo'].strip("v"))
        assert r != None, "User single video GET should succeed for owned video"
        with pytest.raises(Exception):
            vimeo.me.videos.get("1234567")

    def test_user_watchlater(self):
        self.multi_lookup('users', data['user'], 'watchlater')

        self.put_item('users', data['user'], 'watchlater', data['likevideo'])
        self.delete_item('users', data['user'], 'watchlater', data['likevideo'])

        vimeo.me.watchlater.putmulti({"clips": [70899262]})
        vimeo.me.watchlater.get('70899262')
        with pytest.raises(Exception):
            vimeo.me.watchlater.get(data['likevideo'])
        assert True, "Watchlaters PUT should replace all watchlaters"


@pytest.mark.usefixtures("setup")
class TestVideo(VimeoObjectTest):
    def test_videos(self):
        self.search('videos')

    def test_videos_single(self):
        self.single_lookup('videos', data['editvideo'])
        editname = 'iwasedited'
        vimeo.videos.get(data['editvideo']).patch({'name': editname})
        r = vimeo.videos.get(data['editvideo'])()
        if data['editvideo'] in r['body']['link']:
            assert r['body']['name'] == editname
        # reset for next run
        vimeo.videos.get(data['editvideo']).patch({'name': 'Nellie Krumping'})

    def test_video_comments(self):
        self.multi_lookup('videos', data['editvideo'], 'comments')

        pid = self.post_item('videos', data['editvideo'], 'comments', {'text': 'testing text'})
        pid = pid.strip('/comments')

        resources = getattr(vimeo, 'videos')
        resource = getattr(resources, data['editvideo'])
        r = getattr(resource, 'comments').get(pid)
        assert '/'.join(pid.split('/')[-2:]) in r['body']['uri'], "%s should be able to get comments" % (str(resource))

        self.patch_item('videos', data['editvideo'], 'comments', pid, {'text': 'edited text'})
        self.delete_item('videos', data['editvideo'], 'comments', pid)

    def test_video_credits(self):
        self.multi_lookup('videos', data['editvideo'], 'credits')

        pid = self.post_item('videos', data['editvideo'], 'credits',
                {"name": 'tester', "role": "testee"}, key_field='name')
        self.get_item('videos', data['editvideo'], 'credits', pid)
        self.patch_item('videos', data['editvideo'], 'credits', pid, {'role': 'edited text'})
        self.delete_item('videos', data['editvideo'], 'credits', pid)

    def test_video_likes(self):
        self.multi_lookup('videos', data['editvideo'], 'likes')

    def test_video_presets(self):
        self.put_item('videos', data['editvideo'], 'presets', data['presets'], check_get=False)
        self.exists('videos', data['editvideo'], 'presets', data['presets'])
        self.delete_item('videos', data['editvideo'], 'presets', data['presets'], check_get=False)

    def test_video_stats(self):
        stats = vimeo.videos.get(data['editvideo']).stats()
        assert 'stats' in stats['body']

    def test_video_tags(self):
        testtag = "krumping"
        vimeo.videos.get(data['editvideo']).tags.put(testtag)
        vimeo.videos.get(data['editvideo']).tags.get(testtag)
        assert True, "Tag PUT should be able to add a tag"
        vimeo.videos.get(data['editvideo']).tags.delete(testtag)
        with pytest.raises(Exception):
            vimeo.videos.get(data['editvideo']).tags.get(testtag)

        self.multi_lookup('videos', data['editvideo'], 'tags')

        vimeo.videos.get(data['editvideo']).tags.putmulti(['testone', 'testtwo'])
        vimeo.videos.get(data['editvideo']).tags.get('testone')
        with pytest.raises(Exception):
            vimeo.videos.get(data['editvideo']).tags.get(testtag)
        assert True, "Tags PUT should replace all tags"

@pytest.mark.usefixtures("setup")
class TestAlbum(VimeoObjectTest):
    def test_album_search(self):
        with pytest.raises(TypeError):
            vimeo.albums()

    def test_album_single(self):
        self.single_lookup('albums', data['album'])

    def test_album_video(self):
        self.multi_lookup('albums', data['album'], 'videos')

        testvideo = data['editvideo'].strip("v")
        self.put_item('albums', data['album'], 'videos', testvideo)
        self.delete_item('albums', data['album'], 'videos', testvideo)

@pytest.mark.usefixtures("setup")
class TestChannel(VimeoObjectTest):
    def test_channel_search(self):
        self.search('channels')
        self.search('channels', 'test')

    def test_channel_create_delete(self):
        r = vimeo.channels.post({'name': 'testchannel', 'description': 'whatever'})
        cid = r['headers']['Location'].split('/')[-1]
        assert cid, "Channels should be able to create channels"
        vimeo.channels.get(cid).delete()
        r = vimeo.channels()
        for channel in r['body']['data']:
            assert cid not in channel['link'], "Channels should be able to delete channels"

    def test_channels_single(self):
        self.single_lookup('channels', data['channel'])
        editname = 'iwasedited'
        vimeo.channels.get(data['channel']).patch({'name': editname})
        r = vimeo.channels()
        for channel in r['body']['data']:
            if data['channel'] in channel['link']:
                assert channel['name'] == editname
        # reset for next run
        vimeo.channels.get(data['channel']).patch({'name': 'somethingelse'})

    def test_channel_users(self):
        self.multi_lookup('channels', data['channel'], 'users')

    def test_channel_videos(self):
        self.multi_lookup('channels', data['channel'], 'videos')

        testvideo = data['editvideo'].strip("v")
        self.put_item('channels', data['channel'], 'videos', testvideo)
        self.delete_item('channels', data['channel'], 'videos', testvideo)


@pytest.mark.usefixtures("setup")
class TestGroup(VimeoObjectTest):
    def test_group_search(self):
        self.search('groups')
        self.search('groups', 'test')

    def test_group_create_delete(self):
        r = vimeo.groups.post({'name': 'testgroup', 'description': 'whatever'})
        gid = r['body']['link'].split('/')[-1]
        assert r['body']['link'], "Groups should be able to create groups"
        vimeo.groups.get(gid).delete()
        r = vimeo.groups()
        for group in r['body']['data']:
            assert gid not in group['link'], "Groups should be able to delete groups"

    def test_group_single(self):
        self.single_lookup('groups', data['group'])

    def test_group_users(self):
        self.multi_lookup('groups', data['group'], 'users')

    def test_group_videos(self):
        self.multi_lookup('groups', data['group'], 'videos')

        testvideo = data['editvideo'].strip("v")
        self.put_item('groups', data['mygroup'], 'videos', testvideo)
        self.delete_item('groups', data['mygroup'], 'videos', testvideo)


@pytest.mark.usefixtures("setup")
class TestCategory(VimeoObjectTest):
    def test_category_search(self):
        self.search('categories')
        self.search('categories', 'test')

    def test_category_single(self):
        self.single_lookup('categories', data['category'])

    def test_category_channels(self):
        self.multi_lookup('categories', data['category'], 'channels')

    def test_category_groups(self):
        self.multi_lookup('categories', data['category'], 'groups')

    def test_category_users(self):
        self.multi_lookup('categories', data['category'], 'users')

    def test_category_videos(self):
        self.multi_lookup('categories', data['category'], 'videos')

@pytest.mark.usefixtures("setup")
class TestUpload(VimeoObjectTest):
    def test_upload(self):
        old_total = vimeo.me.videos()['body']['total']
        def hook(_range):
            assert _range > 0, "Uploading with a post-check hook should call the hook"
        try:
            uid = vimeo.upload(data['uploadvideo'], post_check_hook=hook)
        except IOError:
            raise IOError("You must create a file in your cwd called testupload.mp4 in order to test uploads")
        total = vimeo.me.videos()['body']['total']
        assert total - 1 == old_total, "Uploading a video should add 1 to user video count"

        vimeo.videos.get(uid).delete()
        r = vimeo.me.videos()
        deleted = True
        for video in r['body']['data']:
            if uid in video['uri']:
                deleted = False
        assert deleted, "Videos should be able to delete videos"
