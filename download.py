# download.py
#
# Download audio from youtube videos
# Developed to be used with playlist.py script
# !!!
# TODO: currently does not work, possibly due to recent
# changes in youtube's api
# !!!
#
# Author: Griffin Mareske gmareske@gmail.com
import re

import requests
from bs4 import BeautifulSoup
import youtube_dl


def find_url(query):
    '''
    Finds a youtube url for a given query string,
    will try to return the most likely one
    I can't search youtube without an api key and
    such and I'm also lazy so here is my hack around
    it.

    Parameters
    ----------

    Returns
    -------
    '''
    # base = 'https://youtube.com/results'
    base = 'https://google.com/search'
    payload = {'q': query.replace(' ', ',')}
    search_results = requests.get(base, params=payload)
    if search_results.status_code == 200:
        text = BeautifulSoup(search_results.text)
        yt_urls = filter_yt_urls(text)
        return yt_urls[0]


def get_vid_id(url):
    '''
    Returns the video id of a youtube url
    '''
    id_re = re.compile('v=(.*)')
    m = id_re.findall(url)
    if m:
        return m[0]
    else:
        print("No match!")


def filter_yt_urls(text):
    link_re = re.compile('https:\/\/www\.youtube\.com\/watch\?v=(.*)')
    yt_urls = [url.text for url in text.find_all('cite')
               if link_re.match(url.text)]
    return yt_urls


def download_tracks(tracks):
    '''
    Download a list of tracks and saves them
    Code stolen ruthlessly from the docs of youtube_dl

    Parameters
    ----------

    Returns
    -------

    '''
    track_urls = [find_url(track) for track in tracks]

    print('Now dowloading the following urls:')
    print('-' * 50)
    for i, c in enumerate(track_urls):
        print('{}: {}'.format(i, c))

    opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
        'netrc': True,
        # progress hooks?
        # logging?
        }
    with youtube_dl.YoutubeDL() as ydl:
        ydl.download(track_urls)
