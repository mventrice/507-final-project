#### unique_name: marielev
#### name: Mariele Ventrice
#### SI507 FINAL PROJECT

import requests
import json
import secrets as secrets
import sqlite3

client_id = secrets.SPOTIFY_API_CLIENT_ID
client_secret = secrets.SPOTIFY_API_SECRET

conn = sqlite3.connect("music.sqlite")
cur = conn.cursor()

CACHE_DICT = {}
CACHE_FILE_NAME = "music_cache.json"

##### Authorization #####
url ="https://accounts.spotify.com/api/token"
data = {'client_id' : client_id,
        'client_secret' : client_secret,
        'grant_type' : 'client_credentials'                 
        }

auth_response = requests.post(url, data)
#Convert response to JSON
auth_response_data = auth_response.json()
#Save the access token
access_token = auth_response_data['access_token']
##### End Authorization #####
HEADERS = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}



############## GETTING DATA FROM APIS & FORMATTING ##############

class Track:
    ''' A music track

    Instance attributes
    -------------------
    genre: list

    track_name: string

    spotify_track_id: string

    track_popularity: integer

    artist_name: string

    album_name: string

    spotify_url: string

    spotify_preview: string

    # danceability: int

    # tempo: int

    # acousticness: int

    # music_video: string

    '''
    def __init__(self, genre="Unknown", track_name="Unknown track", spotify_track_id="None", track_popularity=0, artist_name="Unknown Artist", album_name="Unknown Album", spotify_url="Unknown", preview="Not available", spotify_artist_id="Unknown"):
        self.genre = genre
        self.track_name = track_name
        self.spotify_track_id = spotify_track_id
        self.track_popularity = track_popularity
        self.artist_name = artist_name
        self.album_name = album_name
        self.spotify_url = spotify_url
        self.preview = preview
        self.spotify_artist_id = spotify_artist_id
        # self.danceability = int(danceability) * 100

    def info(self):
        return f"{self.track_name} ({self.album_name}) by {self.artist_name} – {self.spotify_artist_id}" 

class Artist:
    ''' A spotify artist

    Instance attributes
    -------------------
    genre: list

    artist_name: string

    spotify_artist_id: string

    artist_name: string

    TADB_artist_id: string

    '''
    def __init__(self, genre="Unknown", artist_name="Unknown Artist", spotify_artist_id="Unknown", TADB_artist_id="Unknown"):
        self.genre = genre
        self.artist_name = artist_name
        self.TADB_artist_id = TADB_artist_id
        self.spotify_artist_id = spotify_artist_id
        # self.danceability = int(danceability) * 100

    def info(self):
        return f"{self.artist_name} ({self.spotify_artist_id})"

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

def make_spotify_request_with_cache(baseurl, params):
    '''Check the cache for a saved result for api request. If the result is found,
    return it. Otherwise, send a new request, save it, then return it. 

    Parameters
    ----------
    baseurl: string
        The URL for the get request
    cache: dictionary of json data

    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    headers=HEADERS
    CACHE_DICT = open_cache()
    unique_key = construct_unique_key(baseurl, params)
    if (unique_key in CACHE_DICT.keys()):
        print("Using cache")
        return CACHE_DICT[unique_key]
    else:
        print("Fetching")
        response = requests.get(baseurl, params, headers=headers)
        CACHE_DICT[unique_key] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

def make_spotify_audio_features_request_with_cache(search_url):
    headers=HEADERS
    CACHE_DICT = open_cache()
    unique_key = search_url
    if (unique_key in CACHE_DICT.keys()):
        print("Using cache")
        return CACHE_DICT[unique_key]
    else:
        print("Fetching")
        response = requests.get(search_url, headers=headers)
        CACHE_DICT[unique_key] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

def make_spotify_artists_request_with_cache(search_url):
    headers=HEADERS
    CACHE_DICT = open_cache()
    unique_key = search_url
    if (unique_key in CACHE_DICT.keys()):
        print("Using cache")
        return CACHE_DICT[unique_key]
    else:
        print("Fetching")
        response = requests.get(search_url, headers=headers)
        CACHE_DICT[unique_key] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[unique_key]

def get_folk_tracks():
    baseurl="https://api.spotify.com/v1/search"
    params={"q":"genre:folk", "type":"track", "limit":50}
    results = make_spotify_request_with_cache(baseurl, params)
    return results

def get_emo_tracks():
    baseurl="https://api.spotify.com/v1/search"
    params={"q":"genre:emo", "type":"track", "limit":50}
    results = make_spotify_request_with_cache(baseurl, params)
    return results

def get_indie_tracks():
    baseurl="https://api.spotify.com/v1/search"
    params={"q":"genre:indie", "type":"track", "limit":50}
    results = make_spotify_request_with_cache(baseurl, params)
    return results

def get_punk_tracks():
    baseurl="https://api.spotify.com/v1/search"
    params={"q":"genre:punk", "type":"track", "limit":50}
    results = make_spotify_request_with_cache(baseurl, params)
    return results

def get_spotify_artists(spotify_artist_id):
    # spotify_artist_id = artist_object.spotify_artist_id
    baseurl="https://api.spotify.com/v1/artists"
    search_url = baseurl + "/" + spotify_artist_id
    results = make_spotify_artists_request_with_cache(search_url)
    return results

def create_track_objects(spotify_track_results):
    list_track_objects = []
    results_list = spotify_track_results['tracks']['items']
    for i in range(len(results_list)):
        track_name = results_list[i]['name']
        album_name = results_list[i]['album']['name']
        popularity = results_list[i]['popularity']
        preview_url = results_list[i]['preview_url']
        spotify_url = results_list[i]['external_urls']['spotify']
        artist_name = results_list[i]['artists'][0]['name']
        artist_id = results_list[i]['artists'][0]['id']
        track_id = results_list[i]['id']
        track_object = Track(track_name=track_name, spotify_track_id=track_id, track_popularity=popularity, artist_name=artist_name, album_name=album_name, spotify_url=spotify_url, preview=preview_url, spotify_artist_id=artist_id)
        list_track_objects.append(track_object)
    return list_track_objects

def create_artist_objects(spotify_artist_results):
    list_artist_objects = []
    for i in range(len(spotify_artist_results)):
        artist_id = spotify_artist_results[i]['id']
        artist_name = spotify_artist_results[i]['name']
        genre = spotify_artist_results[i]['genres']
        artist_object = Artist(artist_name=artist_name, spotify_artist_id=artist_id, genre=genre, TADB_artist_id="Unknown")
        list_artist_objects.append(artist_object)
    return list_artist_objects

def turn_artist_objects_to_lists(list_artist_objects):
    new_artists_list = []
    for artist in list_artist_objects:
        single_artist_list = []
        single_artist_list.append(artist.artist_name)
        single_artist_list.append("?")
        single_artist_list.append(artist.spotify_artist_id)
        single_artist_list.append("?")
        new_artists_list.append(single_artist_list)
    return new_artists_list


def turn_track_objects_to_lists(list_track_objects):
    new_track_list = []
    for track in list_track_objects:
        single_track_list = []
        single_track_list.append(track.track_name)
        single_track_list.append(track.artist_name)
        single_track_list.append(track.album_name)
        single_track_list.append(track.preview)
        single_track_list.append(track.spotify_url)
        single_track_list.append("?")
        single_track_list.append(track.spotify_artist_id)
        single_track_list.append(track.spotify_track_id)
        new_track_list.append(single_track_list)
    return new_track_list

def get_track_audio_features(track_object):  
    track_id = track_object.spotify_track_id
    baseurl="https://api.spotify.com/v1/audio-features"
    search_url = baseurl + "/" + track_id
    results = make_spotify_audio_features_request_with_cache(search_url)
    return results

# def get_spotify_artists_by_id()

############## CREATING TABLES & INSERTING DATA ##############

drop_tracks = '''
    DROP TABLE IF EXISTS "tracks";
'''

create_tracks = '''
    CREATE TABLE IF NOT EXISTS "tracks" (
        "Id"                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "TrackName"         TEXT NOT NULL,
        "AristName"         TEXT NOT NULL,
        "AlbumName"         TEXT,
        "SpotifyPreview"    TEXT,
        "SpotifyURL"        TEXT,
        "Genre"             TEXT,
        "SpotifyArtistId"   TEXT,
        "SpotifyTrackId"    TEXT NOT NULL
    );
'''

drop_artists = '''
    DROP TABLE IF EXISTS "artists";
'''

create_artists = '''
    CREATE TABLE IF NOT EXISTS "artists" (
        "Id"                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "AristName"         TEXT NOT NULL,
        "Genre"             TEXT,
        "SpotifyArtistId"   TEXT NOT NULL,
        "TadbArtistId"      TEXT NOT NULL
    );
'''

# cur.execute(drop_tracks)
# cur.execute(create_tracks)
# conn.commit()

cur.execute(drop_artists)
cur.execute(create_artists)
conn.commit()



insert_tracks = '''
    INSERT INTO tracks
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
'''

insert_artists = '''
    INSERT INTO artists
    VALUES (NULL, ?, ?, ?, ?)
'''


folk_results = get_folk_tracks()
list_folk_track_objects = create_track_objects(folk_results)

emo_results = get_emo_tracks()
list_emo_track_objects = create_track_objects(emo_results)

indie_results = get_indie_tracks()
list_indie_track_objects = create_track_objects(indie_results)
# # print(list_indie_track_objects[0].info())

punk_results = get_punk_tracks()
list_punk_track_objects = create_track_objects(punk_results)
# # print(list_punk_track_objects[0].info())

full_track_list = list_folk_track_objects + list_indie_track_objects + list_punk_track_objects + list_emo_track_objects
# print(full_track_list)
##Combine the lists here##



### Get Artists ######
artist_list = []
for track in full_track_list:
    spotify_artist_id = track.spotify_artist_id
    results = get_spotify_artists(spotify_artist_id)
    artist_list.append(results)

##### Turn Artists Results into Objects ###

list_artist_objects = create_artist_objects(artist_list)
list_artists_lists = turn_artist_objects_to_lists(list_artist_objects)

for artist in list_artists_lists:
    cur.execute(insert_artists, artist)
conn.commit()

list_of_track_lists = turn_track_objects_to_lists(full_track_list)
# print(list_of_track_lists)

for track in list_of_track_lists:
    cur.execute(insert_tracks, track)
conn.commit()



# for key, val in results.items():
#     print (key)
# audio_features = get_track_audio_features(list_track_objects[0])
# print(audio_features)


# audio_features_baseurl = "https://api.spotify.com/v1/audio-features"
# track_id = "7qq8kZ9lfwHlpHqobvAPhM"
# url = audio_features_baseurl + "/" + track_id
# results = requests.get(url, headers=HEADERS)
# print(results.json())






#Testing search

# search_base_url = "https://api.spotify.com/v1/search"
# params = {"q": "genre:folk", "type":"artist", "limit":"2"}

# response = requests.get(search_base_url, params=params, headers=HEADERS)
# print(response.text)



# response = requests.get("https://api.spotify.com/v1/browse/categories", headers=headers)
# print(response.text)



##########   FOR REFERENCE : SPOTIFY GENRES ########

# genre_results = requests.get("https://api.spotify.com/v1/recommendations/available-genre-seeds", headers=HEADERS)
# print(genre_results.text)
