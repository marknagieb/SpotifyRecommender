import time
from spotipy.exceptions import SpotifyException
import random
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from spotipy.oauth2 import SpotifyOAuth
import pyautogui
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Label, PhotoImage
import webbrowser
from dotenv import load_dotenv
import os


# Spotify API credentials
load_dotenv()
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri = 'http://localhost:8080'

# Authorization flow
scope = 'user-top-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))


# Get user's top tracks
def get_user_top_tracks(user_id, time_range="medium_term", limit=50):
    top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    track_ids = [track["id"] for track in top_tracks["items"]]
    return track_ids


# Get track metadata
def get_track_metadata(track_id):
    track = sp.track(track_id)
    metadata = {
        "id": track["id"],
        "name": track["name"],
        "artists": [artist["name"] for artist in track["artists"]],
        "album": track["album"]["name"],
        "popularity": track["popularity"],
        "duration_ms": track["duration_ms"],
        "explicit": track["explicit"],
    }
    return metadata

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def get_track_ids_from_playlist(playlist_id):
    tracks = get_playlist_tracks(playlist_id)
    track_ids = [track['track']['id'] for track in tracks]
    return track_ids


# Replace this with the ID of a playlist containing a diverse set of songs
playlist_id = "37i9dQZF1DXcBWIGoYBM5M"  # This is the ID of Spotify's "Today's Top Hits" playlist
all_songs = get_track_ids_from_playlist(playlist_id)


# User ID and time range for top tracks
user_id = "marknagieb"
time_range = "medium_term"

# Get user's top tracks and track metadata
top_track_ids = get_user_top_tracks(user_id, time_range=time_range)
tracks_metadata = [get_track_metadata(track_id) for track_id in top_track_ids]

# Define the rating scale (1 to 5)
reader = Reader(rating_scale=(1, 5))

# Load the dataset from the top tracks metadata
data = []
for track in tracks_metadata:
    data.append((user_id, track["id"], random.randint(3, 5)))

dataset = Dataset.load_from_df(pd.DataFrame(data, columns=["user_id", "song_id", "rating"]), reader)

# Split the dataset into train and test sets
trainset, testset = train_test_split(dataset, test_size=0.2)

# Train the model using KNNBasic algorithm
algo = KNNBasic()
algo.fit(trainset)

# Test the model
predictions = algo.test(testset)


# Get a list of all song ids
all_songs = list(set([x[1] for x in data]))

# Get track IDs for previous listens
previous_listens = pd.DataFrame(data, columns=["user_id", "song_id", "rating"])
previous_listens = previous_listens[previous_listens["user_id"] == user_id]
track_ids = previous_listens["song_id"].tolist()

# Use track IDs to get track features
track_features = []
for i in range(0, len(track_ids), 50):
    try:
        audio_features = sp.audio_features(track_ids[i:i+50])
        # Your code to process the audio_features data
    except SpotifyException as e:
        if e.http_status == 429:
            # Get the Retry-After header value (in seconds) and add some extra time as a buffer
            retry_after = int(e.headers.get('Retry-After', 1)) + 1
            print(f"Rate limit exceeded, waiting for {retry_after} seconds")
            time.sleep(retry_after)
        else:
            print(f"An error occurred: {e}")


# Preprocess audio features
track_features_df = pd.DataFrame(track_features)
# Preprocess audio features (continued)
track_features_df = (track_features_df - track_features_df.mean()) / track_features_df.std()
columns_to_drop = ["type", "id", "uri", "track_href", "analysis_url"]
columns_to_drop = [col for col in columns_to_drop if col in track_features_df.columns]
track_features_df = track_features_df.drop(columns=columns_to_drop)


# Use trained model to predict ratings for new songs
new_ratings = []
for song_id in all_songs:
    rating = algo.predict(user_id, song_id, r_ui=None, verbose=False)
    new_ratings.append({"song_id": song_id, "rating": rating.est})


# Get recommended songs
recommended_songs = sorted(new_ratings, key=lambda x: x["rating"], reverse=True)

def show_recommendations():
    top_10_recommended_songs = recommended_songs[:10]

    # Create a themed tkinter window with Spotify colors
    root = tk.Tk()
    root.withdraw()

    # Set the background and foreground colors to match Spotify's green color
    root.config(bg='#282828')

    # Add a Spotify logo image to the top of the window
    logo_img = PhotoImage(file="spotify_logo.png")
    logo_img = logo_img.subsample(4, 4)
    logo_label = Label(root, image=logo_img, bg='#282828')
    logo_label.image = logo_img
    logo_label.pack()


    # Add a label for each recommended song with a hyperlink to the song's page on Spotify's website
    for idx, rec in enumerate(top_10_recommended_songs):
        song_name = get_track_metadata(rec['song_id'])['name']
        song_url = f"https://open.spotify.com/track/{rec['song_id']}"
        rating = f"{rec['rating']:.2f}"

        label_frame = tk.Frame(root, bg='#282828')
        label_frame.pack(pady=(20, 0))

        song_name_label = Label(label_frame, text=f"{idx + 1}. {song_name}", font=('Helvetica', 16), fg='#1DB954', bg='#282828')
        song_name_label.pack(side=tk.LEFT)

        song_link_label = Label(label_frame, text="Listen on Spotify", font=('Helvetica', 14), fg='#1DB954', bg='#282828', cursor='hand2')
        song_link_label.pack(side=tk.LEFT, padx=(10, 0))
        song_link_label.bind("<Button-1>", lambda event, url=song_url: webbrowser.open_new(url))

        rating_label = Label(label_frame, text=f"Predicted rating: {rating}", font=('Helvetica', 14), fg='#FFFFFF', bg='#282828')
        rating_label.pack(side=tk.RIGHT, padx=(0, 20))
    # Create a button with Spotify's green color
    button = tk.Button(root, text="Close", command=root.destroy, font=('Helvetica', 14), bg='#1DB954', fg='#FFFFFF')
    button.pack(pady=20)

    # Set the size of the window
    root.geometry("2500x1750")

    # Center the window on the screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.deiconify()
    root.mainloop()

show_recommendations()