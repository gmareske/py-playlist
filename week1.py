#!/usr/bin/env python
# week1.py
#
# The playlist script
# also contains utilities for working with musicbrainz scripts
#
# Author: Griffin Mareske gmareske@gmail.com
import sys

import musicbrainzngs as mb
from random import choice

from pprint import pprint
import json

# set this to your website, so the mb api has something to reference
USER_WEBSITE = 'https://gmareske.github.io'
mb.set_useragent('py-playlist', '0.1', USER_WEBSITE)

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

    Postconditions
    --------------
    the return value does not contain any duplicate recording titles

    '''
    recs = list()  # return value
    titles = set()  # set of already seen titles to remove duplicates
    recordings = mb.browse_recordings(artist, limit=100,
                                      includes=includes)
    recs += recordings['recording-list']
    count = recordings['recording-count'] - 100  # already grabbed
    offset = 100
    print('Downloading {}...'.format(artist))
    while count >= 0:
        recordings = mb.browse_recordings(artist, limit=100,
                                          includes=includes,
                                          offset=offset)
        # have we already seen a recording of this name?
        for record in recordings['recording-list']:
            if not (record['title'] in titles):
                recs.append(record)
        # update already seen titles
        titles.update([record['title']
                       for record in recordings['recording-list']])
        count -= 100
        offset += 100

    return recs


def filter_collabs(recordings):
    '''
    From a list of recordings, filters out all recordings
    except those that are a collaboration between artists.
    In this case, collabs are anything with less than two
    artists in the credits
    Also cleans up junk in artist credits

    Parameters
    ----------
    recordings : [{...}]
      list of dicts that represent a collection of
      musicbrainz recordings with artist credits

    Returns
    -------
    recordings : [{...}]
      list of dicts that represent a collection of
      musicbrainz recordings with artist credits

    Postconditions
    --------------
    There will only be recordings returned that have more
    than one artist in the credits.
    Junk from musicbrainz in the artist-credits will also be
    removed from all recordings.
    '''
    for record in recordings:
        record['artist-credit'] = [a for a in record['artist-credit']
                                   if type(a) is dict]
    # filter out non-collabs
    # delete anything that has less than two artist
    return [r for r in recordings if len(r['artist-credit']) >= 2]

def get_artists(recording):
    '''
    Returns a list of all artists on one recording

    Parameters
    ----------
    recording : {...}

    Returns
    -------
    artists : [{...}]

    '''
    return [a['artist'] for a in recording['artist-credit']]


def artists_from_recs(original, recordings):
    '''
    Returns a list of all artists featured on all recordings
    except for the original artist, given as a param

    Parameters
    ----------
    original : str
      a string representing the musicbrainz id of an artist
    recordings : [{...}]
      a list of dicts, which holds the musicbrainz recordings
      with artist credits

    Returns
    -------
    artists : [{...}]
      a list of dicts, where each dict is a musicbrainz artist

    Postconditions
    --------------
    artists contains none of original artists
    each artist is in the return list once
    '''
    artists = list()
    for record in recordings:
        artists += [a for a in get_artists(record) if not a['id'] == original]
    # only return unique elements
    return list({a['id']: a for a in artists}.values())


def gen_playlist(seed, lvl=0, maxlvl=50, previous_ids=[]):
    '''
    Recursively generates a list of songs
    in order that match my criteria

    Parameters
    ----------

    Returns
    -------
    '''
    # add current artists to already-seen ids
    previous_ids.append(seed)
    if lvl == maxlvl:
        return list()
    collabs = filter_collabs(get_all_recordings(seed))
    if collabs:
        next_song = choice(collabs)
        # all artists on a song except already visited ones
        fartists = [a['id'] for a in get_artists(next_song)
                    if not a['id'] in previous_ids]
        if not fartists:
            return list()  # no more artists to continue the chain :(
        next_artist = choice(fartists)
        previous_ids.append(seed)
        return [next_song] + gen_playlist(next_artist, lvl=lvl + 1,
                                          previous_ids=previous_ids)

    else:
        return list()


def pprint_playlist(playlist):
    print("Begin playlist")
    print("-" * 20)
    print("Song: {} - {}".format(
        playlist[0]['title'], playlist[0]['artist-credit-phrase']))

    for song in playlist[1:]:
        print("Song: {} - {}".format(
            song['title'], song['artist-credit-phrase']))

if __name__ == '__main__':
    # below are some defined constants to play around with

    # To generate a playlist with your own seed artist,
    # you need to get the musicbrainz 'id' for that artist
    # which can be found by searching for the artist on the musicbrainz
    # website, and copying the id from the url at their page.
    BOB = '72c536dc-7137-4477-a521-567eeb840fa8'
    KANYE = '164f0d73-1234-4e2c-8743-d77bf2191051'
    ORNETTE = '169c0d1b-fcb8-4a43-9097-829aa7b39205'
    GLASPER = '6e8f82ea-9e6d-4fdd-9b32-32feef13186b'
    COREA   = '8446fcca-109e-4c6d-a2ff-5a269b32b4c2'
    HERBIE  = '27613b78-1b9d-4ec3-9db5-fa0743465fdd'
    EWF     = '535afeda-2538-435d-9dd1-5e10be586774'
    LENNON  = '4d5447d7-c61c-4120-ba1b-d7f471d385b9'
    MILES   = '561d854a-6a28-4aa7-8c99-323e6ce46c2a'
    EAGLES  = 'f46bd570-5768-462e-b84c-c7c993bbf47e'
    BOWIE   = '5441c29d-3602-4898-b1a1-b77fa23b8e50'
    WONDER  = '1ee18fb3-18a6-4c7f-8ba0-bc41cdd0462e'
    ACDC    = '66c662b6-6e2f-4930-8610-912e24c63ed1'
    MARIAH  = '494e8d09-f85b-4543-892f-a5096aed1cd4'
    VINCEG  = '05b5488d-7141-4b21-819b-d4713abf2a98'

    # print playlist using seed artist
    pprint_playlist(gen_playlist(KANYE))
