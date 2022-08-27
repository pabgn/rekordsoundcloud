import untangle
import json
def get_playlists(library):
    obj = untangle.parse(library)
    return [playlist['Name'] for playlist in obj.DJ_PLAYLISTS.PLAYLISTS.children[0].children]


def get_collection_data(library):
    obj = untangle.parse(library)
    return {'total_tracks':int(len(obj.DJ_PLAYLISTS.COLLECTION.children)),
            'soundcloud_tracks': [track for track in obj.DJ_PLAYLISTS.COLLECTION.children if 'localhostsoundcloud' in track['Location']]}

def get_settings():
    try:
        with open('settings.json') as json_file:
            return json.load(json_file)
    except:
        return None