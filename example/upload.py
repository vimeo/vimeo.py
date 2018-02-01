import json
import os
import vimeo

config_file = os.path.dirname(os.path.realpath(__file__)) + '/config.json'
config = json.load(open(config_file))

if 'client_id' not in config or 'client_secret' not in config:
    raise Exception('We could not locate your client id or client secret ' +
                    'in `' + config_file + '`. Please create one, and ' +
                    'reference `config.json.example`.')

# Instantiate the library with your client id, secret and access token
# (pulled from dev site)
client = vimeo.VimeoClient(
    token=config['access_token'],
    key=config['client_id'],
    secret=config['client_secret']
)

# Create a variable with a hard coded path to your file system
file_name = '<full path to a video on the filesystem>'

print 'Uploading: %s' % file_name

try:
    # Upload the file and include the video title and description.
    uri = client.upload(file_name, data={
        'name': 'Vimeo API SDK test upload',
        'description': "This video was uploaded through the Vimeo API's " +
                       "Python SDK."
    })

    # Get the metadata response from the upload and log out the Vimeo.com url
    video_data = client.get(uri + '?fields=link').json()
    print '"%s" has been uploaded to %s' % (file_name, video_data['link'])

    # Make an API call to edit the title and description of the video.
    client.patch(uri, data={
        'name': 'Vimeo API SDK test edit',
        'description': "This video was edited through the Vimeo API's " +
                       "Python SDK."
    })

    print 'The title and description for %s has been edited.' % uri

    # Make an API call to see if the video is finished transcoding.
    video_data = client.get(uri + '?fields=transcode.status').json()
    print 'The transcode status for %s is: %s' % (
        uri,
        video_data['transcode']['status']
    )
except vimeo.exceptions.VideoUploadFailure as e:
    # We may have had an error. We can't resolve it here necessarily, so
    # report it to the user.
    print 'Error uploading %s' % file_name
    print 'Server reported: %s' % e.message