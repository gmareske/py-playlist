#!/usr/bin/env python
import sys

import musicbrainzngs as mb
from random import choice

# testing
KANYE = '164f0d73-1234-4e2c-8743-d77bf2191051'
mb.set_useragent('Playlist.py', '0.1', 'https://gmareske.github.io')
from pprint import pprint
import json

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
        print(count)
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


def gen_playlist(seed, lvl=0, maxlvl=10, previous_ids=[]):
    '''
    Recursively generates a list of songs
    in order that match my criteria

    Parameters
    ----------

    Returns
    -------
    '''
    if lvl == maxlvl:
        print("Max recursive level")
        return list()
    collabs = filter_collabs(get_all_recordings(seed))
    # debugging / logging
    print("Currently on {}:".format(seed))
    if collabs:
        next_song = choice(collabs)
        print("Next Song: {}".format(next_song))
        return [next_song] + gen_playlist(choice(
            # random artist from next_song, filtering the original artist out
            [a['id'] for a in get_artists(next_song) if not a['id'] == seed]),
                                          lvl + 1)  # increase recursive level
    else:
        print("Artist {} has no collaborations!".format(seed))
        return []


def pprint_playlist(playlist):
    print("Begin playlist")
    print("-" * 20)
    print("Song: {} - {}".format(
        playlist[0]['title'], playlist[0]['artist-credit-phrase']))

    for song in playlist[1:]:
        print("Song: {} - {}".format(
            song['title'], song['artist-credit-phrase']))

# if __name__ == '__main__':
#     if not seed_artist:
#         seed_artist=input('Enter an artist to start the chain with')
#     else:
#         if mbid:
#             gen_playlist(seed_artist)
