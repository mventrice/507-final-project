from flask import Flask, render_template, request
import sqlite3

def get_tracks_by_genre(genre): 
    '''
    Constructs and executes SQL to retrieve all
    tracks in a user-identified set of genres

    Parameters
    ----------
    list
        List of genres selected by user

    Returns
    ----------
    list
        a list of songs in selected genres
    '''
    connection = sqlite3.connect('music.sqlite')
    cursor = connection.cursor()
    query = '''
        SELECT TrackName, tracks.ArtistName, artists.Genre, artists.ImageUrl, tracks.Popularity, features.Tempo, features.Acousticness FROM tracks
        JOIN artists
        ON tracks.SpotifyArtistId=artists.SpotifyArtistId
        JOIN features
        ON tracks.SpotifyTrackId = features.SpotifyTrackId
        WHERE artists.Genre LIKE ?
        ORDER BY Popularity DESC
    '''
    result = cursor.execute(query, (genre,)).fetchall()
    connection.close()
    return result

def define_tempo(tracks):
    for track in tracks:
        if float(track[-2])>=150:
            tempo = "fast"
        elif float(track[-2]) <= 100:
            tempo = "slow"

def filter_by_tempo(tracks, input_tempo):
    fast_filtered_tracks = []
    slow_filtered_tracks = []
    all_tracks = tracks
    if input_tempo =='fast':
        for track in tracks:
            if float(track[-2])>=150:
                fast_filtered_tracks.append(track)
        return fast_filtered_tracks
    elif input_tempo == 'slow':
        for track in tracks:
            if float(track[-2])<=100:
                slow_filtered_tracks.append(track)
        return slow_filtered_tracks
    else:
        return all_tracks

# def get_music_video()


app = Flask(__name__)
@app.route('/')
def index():
    return render_template("inputs.html")

@app.route('/handle_form', methods=['GET', 'POST'])
def handle_the_form():
    genre = '%' + request.form['genre'] + '%' #holds data to most recent data that has come into app
    # acousticness = request.form['acoustic']
    tempo = request.form['tempo']
    tracks = get_tracks_by_genre(genre)
    tempo_filtered_tracks = filter_by_tempo(tracks,tempo)
    return render_template('response.html', 
        genre=genre.strip("%"),
        # acousticness=acousticness,
        tempo=tempo,
        tracks=tempo_filtered_tracks[0:11]
    )




if __name__ == "__main__":
    app.run(debug=True) 