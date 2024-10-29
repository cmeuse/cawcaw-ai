import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='.env.local')

# Constants from local environment
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SCOPE = 'playlist-read-private playlist-read-collaborative user-library-read'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
PLAYLIST_URL = 'https://api.spotify.com/v1/playlists/'
FEATURES_URL = 'https://api.spotify.com/v1/audio-features?ids='

# Function to get the access token
def get_access_token():
    auth_response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    )
    print(f"Status Code: {auth_response.status_code}")
    print(f"Response: {auth_response.json()}")
    return auth_response.json()['access_token']

# Function to get playlist details
def get_playlist(playlist_id, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(PLAYLIST_URL + playlist_id, headers=headers)
    return response.json()

# Function to download images
def download_image(url, folder, image_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder, image_name), 'wb') as f:
            f.write(response.content)

# Function to get audio features for tracks
def get_audio_features(track_ids, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    features_response = requests.get(FEATURES_URL + ','.join(track_ids), headers=headers)
    return features_response.json()['audio_features']

# Main function
def main(playlist_id):
    # Create folders for images
    track_folder = 'track_images'
    os.makedirs(track_folder, exist_ok=True)

    # Get access token
    token = get_access_token()

    # Get playlist details
    playlist_data = get_playlist(playlist_id, token)
    
    if 'tracks' not in playlist_data:
        print('Invalid Playlist ID or Access Denied')
        return

    # Prepare data for CSV
    songs = []

    # Get track IDs for audio features
    track_ids = []
    
    for item in playlist_data['tracks']['items']:
        track = item['track']
        track_ids.append(track['id'])  # Collecting track IDs for audio features
        song_data = {
            'ID': track['id'],
            'Song Name': track['name'],
            'Artist': ', '.join([artist['name'] for artist in track['artists']]),
            'Cover Image URL': track['album']['images'][0]['url']
        }
        songs.append(song_data)

        # Download track image for each song
        track_image_url = track['album']['images'][0]['url']  # Get the track's cover image
        download_image(track_image_url, track_folder, f"{track['id']}.jpg")  # Save track image

    # Get audio features
    audio_features = get_audio_features(track_ids, token)

    for i, feature in enumerate(audio_features):
        if feature:  # Check if feature is not None
            songs[i].update({
                'Danceability': feature['danceability'],
                'Energy': feature['energy'],
                'Loudness': feature['loudness'],
                'Speechiness': feature['speechiness'],
                'Acousticness': feature['acousticness'],
                'Instrumentalness': feature['instrumentalness'],
                'Liveness': feature['liveness'],
                'Valence': feature['valence'],
                'Tempo': feature['tempo'],
            })

    # Save to CSV
    df = pd.DataFrame(songs)
    df.to_csv(f"{playlist_id}_songs.csv", index=False)

if __name__ == "__main__":
    # Replace with your desired playlist ID
    playlist_id = '1C8RuvGfRsX1fmxaehox9K'  
    main(playlist_id)
