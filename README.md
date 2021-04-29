# Mariele's Music Flask App

## Description

Mariele's Music Flask web application lets users select a genre and a preferred category (e.g. most popular, most obscure, most danceable, slowest temp, more danceable, random). It then displays the top 10 results for those selections in a table that includes the track name, album name, artist name, an image of the artist, and Spotify ratings/assessments for popularity, tempo, and danceability. Then, the user selects one of those 10 tracks. If a music video is available, the user can choose between following a link to the music video on YouTube or following a link to the open Spotify web player. If there are no music videos available, the app says so and offers the Spotify link only. I’ve also embedded the YouTube videos, if they exist. However, the embedded videos will not play on the local Flask development server. 

## Packages
The following Python packages are required: 
* Flask
* requests
* sqlite3

## Usage Instructions

First, pip install any packages. 

git clone https://github.com/mventrice/507-final-project \
cd 507-final-project/ \
python3 music_flask_app.py 


