import untangle
import requests
import subprocess
import time
import re
from urllib.parse import quote
import yt_dlp
from utils import get_collection_data, get_settings

settings = None
def update_library(library, trackId, newLocation):
    fin = open(library, "rt")
    data = fin.read()
    data = data.replace('soundcloud:tracks:'+trackId, quote(newLocation))
    fin.close()
    fin = open(library, "wt")
    fin.write(data)
    fin.close()

def download(trackId, name, location, status_callback, soundcloud_oauth):
    link = None
    status_callback({'status':'metadata', 'filename':name})
    try:
        r = requests.get('https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/'+trackId)
        link = r.text.split('<link rel="canonical" href="')[1].split('">')[0]
    except:
        status_callback({'status':'error', 'message':'Could not obtain track data from SoundCloud', 'filename':name})

    if link:
        URLS = [link]

        ydl_opts = {
            "quiet": True,
            'writethumbnail': True,
            'addMetadata': True,
            'progress_hooks': [status_callback],
            'format': 'bestaudio',
            'username': 'oauth',
            'password': soundcloud_oauth,
            'outtmpl': location+'/'+name+'.%(ext)s',
            'postprocessors': [{  
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            },
            {'key': 'EmbedThumbnail', },
            {'key': 'FFmpegMetadata', 'add_metadata': True, }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(URLS)
            return name+'.mp3'
    else:
        return None

def translate(library, songs_folder, progress_callback, status_callback):
    settings = get_settings()
    if settings and settings['soundcloud_oauth']:
        collection_data = get_collection_data(library)
        total_soundcloud_tracks = len(collection_data['soundcloud_tracks'])
        status_callback({'status':'initial', 'total_tracks':collection_data['total_tracks'], 'total_soundcloud_tracks':total_soundcloud_tracks})
        converted = 0
        errors = 0
        for track in collection_data['soundcloud_tracks']:
            trackId = track['Location'].split(":")[3]
            print(trackId)
            song = download(trackId, track['Name'], songs_folder, status_callback, settings['soundcloud_oauth'])
            if song:
                newLocation = songs_folder+'/'+song
                update_library(library, trackId, newLocation)
                converted+=1
            else:
                errors+=1
            progress = ((converted + errors)/ total_soundcloud_tracks)
            progress_callback(progress)
        status_callback({'status':'end', 'converted':converted, 'errors':errors})
    else:
        status_callback({'status':'fatal', 'message':'SoundCloud OAuth password not provided. Check settings.json and try again'})
