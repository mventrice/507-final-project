from flask import Flask, render_template, request
import sqlite3
import requests
import json
import random

CACHE_DICT = {}
CACHE_FILE_NAME = "music_cache.json"

class MusicVideo:
    ''' A Music Video

    Instance attributes
    -------------------
    mvid_url (str): URL to YouTube video from The AudioDatabase API
    
    track_name (str): Name of track from The AudioDatabase API
    
    tadb_artist_id (str): Id of artist the The AudioDatabase API

    '''
    def __init__(self, mvid_url="None", track_name="None", tadb_artist_id="None"):
        self.mvid_url = mvid_url
        self.track_name = track_name
        self.tadb_artist_id = tadb_artist_id

    def info(self):
        '''
        Returns string literal of object instance.

        Parameters
        ----------
        none

        Returns
        ----------
        Object instance formatted as <track_name>, <tadb_artist_id> – <mvid_url>
        '''
        return f"{self.track_name}, {self.tadb_artist_id} – {self.mvid_url}"

def get_tracks_by_genre(genre):
    '''
    Constructs and executes SQL to retrieve all
    tracks in a user-identified set of genres

    Parameters
    ----------
    genre (list)
        a list of genres selected by user

    Returns
    ----------
    list
        a list of songs in selected genres
    '''
    connection = sqlite3.connect('music.sqlite')
    cursor = connection.cursor()
    query = '''
        SELECT TrackName, tracks.ArtistName, artists.Genre, artists.ImageUrl, tracks.AlbumName, tracks.Popularity, features.Tempo, features.Danceability FROM tracks
        JOIN artists
        ON tracks.SpotifyArtistId=artists.SpotifyArtistId
        JOIN features
        ON tracks.SpotifyTrackId = features.SpotifyTrackId
        WHERE artists.Genre LIKE ?
    '''
    result = cursor.execute(query, (genre,)).fetchall()
    connection.close()
    return result

def get_spotify_player_url(track_name):
    '''
    Constructs and executes SQL to retrieve Spotify URL
    from tracks table in music.sqlite.

    Parameters
    ----------
    track_name (str)
        The name of a track

    Returns
    ----------
    list
        a list of tuples containing spotify player url
    '''
    connection = sqlite3.connect('music.sqlite')
    cursor = connection.cursor()
    query = '''
    SELECT SpotifyURL FROM tracks
    WHERE TrackName = ?
    '''
    result = cursor.execute(query, (track_name,)).fetchall()
    connection.close()
    return result

def sort_by_danceability(tracks):
    '''
    Sorts tracks by Spotify danceability assessment.

    Parameters
    ----------
    tracks (list)
        a list of tracks (tuples) to be sorted

    Returns
    ----------
    list
        returns the sorted list
    '''
    tracks.sort(key = lambda x: x[-1]) 
    return tracks.reverse()

def sort_by_slowest(tracks):
    '''
    Sorts tracks by Spotify speed, with slowest first.

    Parameters
    ----------
    tracks (list)
        a list of tracks (tuples) to be sorted

    Returns
    ----------
    list
        returns the sorted list
    '''
    tracks.sort(key = lambda x: x[-2]) 
    return tracks

def sort_by_popularity(tracks):
    '''
    Sorts tracks by Spotify popularity; most popular first

    Parameters
    ----------
    tracks (list)
        a list of tracks (tuples) to be sorted

    Returns
    ----------
    list
        returns the sorted list
    '''
    tracks.sort(key = lambda x: x[-3]) 
    return tracks.reverse()

def sort_by_obscurity(tracks):
    '''
    Sorts tracks by Spotify popularity; least popular first

    Parameters
    ----------
    tracks (list)
        a list of tracks (tuples) to be sorted

    Returns
    ----------
    list
        returns the sorted list
    '''
    tracks.sort(key = lambda x: x[-3]) 
    return tracks

def sort_random(tracks):
    '''
    Sorts tracks randomly, using random module.

    Parameters
    ----------
    tracks (list)
        a list of tracks (tuples) to be sorted

    Returns
    ----------
    list
        returns the sorted (shuffled) list
    '''
    random.shuffle(tracks)
    return tracks

def filter_artists(track_list):
    '''
    Gets a list of just the artists in a track list

    Parameters
    ----------
    tracks (list)
        a list of tracks

    Returns
    ----------
    list
        returns a list of artists
    '''
    artists = []
    for track in track_list:
        artists.append(track[1])
    return artists

def remove_duplicate_artists(artists_list):
    '''
    removes duplicate artists from list of artists

    Parameters
    ----------
    tracks (list)
        a list of artists

    Returns
    ----------
    list
        returns the sorted (shuffled) list
    '''
    i = 0
    while i < len(artists_list):
      j = i + 1
      while j < len(artists_list):
         if artists_list[i] == artists_list[j]:
            del artists_list[j]
         else:
            j += 1
      i += 1

def open_cache():
    '''Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary. If the cache file doesn't exist, creates
    a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The loaded cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    contents_to_write = json.dumps(cache)
    cache_file = open(CACHE_FILE_NAME, 'w')
    cache_file.write(contents_to_write)
    cache_file.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []  #empty list to store parameter strings (unique keys)
    connector = "_"
    for key in params.keys(): #for key in key value pair
        param_strings.append(f"{key}_{params[key]}") #adds key, value pair of each paramater as key_value
    param_strings.sort() #sorts list so keys are in order
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_artist_request(artist):
    ''' gets a list of artists from The Audio Database API.
    Uses cache if requests exists in cache.

    Parameters
    ----------
    artist (str)
        The name of an artist (leave spaces in)

    Returns
    -------
    dict:
        json formatted results from request
    '''
    CACHE_DICT = open_cache()
    baseurl = "https://www.theaudiodb.com/api/v1/json/1/search.php"
    params = {"s": artist}
    unique_key = construct_unique_key(baseurl, params)
    if (unique_key in CACHE_DICT.keys()):
        return CACHE_DICT[unique_key]
    else:
        response = requests.get(baseurl, params=params)
        CACHE_DICT[unique_key] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

def make_music_video_request(artist_id):
    ''' gets music videos by a particular artist

    Parameters
    ----------
    artist (str)
        TADB artist ID

    Returns
    -------
    dict:
        json formatted results from request
    '''
    CACHE_DICT = open_cache()
    baseurl = "https://theaudiodb.com/api/v1/json/1/mvid.php"
    params = {"i": artist_id}
    unique_key = construct_unique_key(baseurl, params)
    if (unique_key in CACHE_DICT.keys()):
        return CACHE_DICT[unique_key]
    else: 
        response = requests.get(baseurl, params=params)
        CACHE_DICT[unique_key] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

def get_artist_tadb_id(artist):
    ''' gets artist ID by using make_artists_request and 
        parsing results.

    Parameters
    ----------
    artist (str)
        The name of an artist (leave spaces in)

    Returns
    -------
    list:
        list of artists ids
    '''
    artist_id_list = []
    results = make_artist_request(artist)
    if results['artists'] != None:
        artist_id = results['artists'][0]["idArtist"]
        artist_id_list.append(artist_id)
    else:
        artist_id = "Unknown"
    return artist_id_list

def get_music_videos(artist_id):
    ''' gets artist ID by using make_music_video request
    and parsing results.

    Parameters
    ----------
    artist (str)
        artist id

    Returns
    -------
    list:
        list of MusicVideo objects
    '''
    mvid_objects_list = []
    results = make_music_video_request(artist_id)
    if results['mvids'] != None:
        for i in range(len(results['mvids'])):
            track_name = results['mvids'][i]['strTrack']
            mvid_url = results['mvids'][i]['strMusicVid']
            artist_id = artist_id
            mvid_object = MusicVideo(mvid_url=mvid_url, track_name=track_name, tadb_artist_id=artist_id)
            mvid_objects_list.append(mvid_object)
    return mvid_objects_list


app = Flask(__name__)
@app.route('/')
def index():
    return render_template("inputs.html")

@app.route('/results', methods=['GET', 'POST'])
def handle_the_form():
    genre = '%' + request.form['genre'] + '%' 
    sort = request.form['sort']
    tracks = get_tracks_by_genre(genre)
    if sort == "popularity":
        sort_by_popularity(tracks)
    elif sort == "obscurity":
        sort_by_obscurity(tracks)
    elif sort == "danceability":
        sort_by_danceability(tracks)
    elif sort == "speed (slow)": 
        sort_by_slowest(tracks)
    else:
        sort_random(tracks)
    return render_template('response.html', 
        genre=genre.strip("%"),
        sort = sort,
        tracks=tracks[0:11],
    )

@app.route('/play-music', methods=['GET', 'POST'])
def play_music():
    selection = request.form['selection']
    track_artist_list = selection.split("+")
    track = track_artist_list[0]
    artist = track_artist_list[1]
    spotify_url = get_spotify_player_url(track)
    spotify_url = spotify_url[0][0]
    youtube_url = 'None'
    artist_results = get_artist_tadb_id(artist)
    if len(artist_results) > 0:
        music_videos = get_music_videos(artist_results[0])
        for music_video in music_videos:
            if music_video.track_name in track:
                youtube_url = music_video.mvid_url
                break
    return render_template("play-music.html",
        spotify_url=spotify_url,
        youtube_url=youtube_url,
        track=track,
        artist=artist,
        )

if __name__ == "__main__":
    app.run(debug=True) 