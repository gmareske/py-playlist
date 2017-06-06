#!/usr/bin/env python

# exploration of musicbrainz api with python
# goal is to generate a playlist of songs
# where each song shares one artist in common
# with the song before and after it

import musicbrainzngs as mb
from pprint import pprint

KANYE = '164f0d73-1234-4e2c-8743-d77bf2191051'
mb.set_useragent('Playlist.py', '0.1', 'https://gmareske.github.io')

# pprint(mb.browse_recordings(KANYE, limit=100, offset=100))

def print_all_release_names(artist):
    # artist is a mb artist id
    releases = mb.browse_releases(artist, limit=1,includes=['artist-rels'])
    pprint(releases)
    count = releases['release-count']
    offset = 0
    names = list()
    while count > 0:
        releases = mb.browse_releases(artist, limit=100, offset=offset)
        names.append([release['title'] for release in releases['release-list']])
        count -= 100

    pprint(names)


# Note: due to mb's api rate limiting, this procedure runs slowly
# and only make one request per second to avoid getting blacklisted
# This means 100 recordings are processed per sec
#
# so don't be afraid if your program has a bottleneck at this point
# TODO: maybe implement some kind of progress update
def get_all_recordings(artist, includes=['artist-credits']):
    '''
    Gets all recordings by an artist with default artist credits

    Parameters
    ----------
    artist : str
      This should be a musicbrainz id str representing the artist
    includes : [str]
      list of include parameters matching the parameters at
      https://wiki.musicbrainz.org/Development/XML_Web_Service/Version_2#Libraries_to_use_the_Web_Service

    Returns
    -------
    recs : [{...}]
    a list of dicts, where each dict is a recording done by (at least)
    the artist

    '''
    recs = list()
    recordings = mb.browse_recordings(artist, limit=100,
                                      includes=includes)
    recs += recordings['recording-list']
    count = recordings['recording-count'] - 100 # already grabbed
    offset = 100
    while count >= 0:
        recordings = mb.browse_recordings(artist, limit=100,
                                          includes=includes,
                                          offset=offset)
        recs += recordings['recording-list']
        count -= 100
        print(count)
        offset += 100

    return recs
