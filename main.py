import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser

# Read song names from the playlist text file
with open('playlist.txt', 'r') as f:
    playlist = f.readlines()

# Extract track names from the playlist file and format them
song_names = []
for line in playlist:
    try:
        dash = line.find("-")
        track_name = line[0:dash-1]
        artist_name = line[dash+1:]
        song_names.append([track_name, artist_name])  # 0: track name     1: artist name
    except ValueError:
        print(f"Skipping line due to formatting issue: {line.strip()}")
        continue

for i in range(len(song_names)):
    print(f"{song_names[i][0]} by {song_names[i][1]}")

   
# Initialize Spotify OAuth with your credentials
sp_oauth = SpotifyOAuth(
    client_id='841ba12129b546c9a100fa42493516fb',
    client_secret='e256383affd642fc83b09006cfb66d51',
    redirect_uri='http://localhost:8888/callback',  # Ensure this matches your Spotify Developer Dashboard settings
    scope=["playlist-modify-public", "playlist-modify-private", "user-library-modify"]
)

# Attempt to retrieve token info
token_info = sp_oauth.get_cached_token()

if not token_info:
    # Generate and print the authorization URL
    auth_url = sp_oauth.get_authorize_url()
    print("Please visit this URL to authorize:", auth_url)

    # Open the authorization URL in the default browser
    webbrowser.open(auth_url)

    # Prompt user to paste the redirected URL after authorization
    redirect_response = input("Paste the full redirect URL here: ")
    code = sp_oauth.parse_response_code(redirect_response)
    token_info = sp_oauth.get_access_token(code)

# Initialize the Spotify API client with the access token
sp = spotipy.Spotify(auth=token_info['access_token'])
print("Authenticated successfully!")

# Get the authenticated user Spotify ID
user_id = sp.me()["id"]

# Prompt for a new playlist name and create it on Spotify
new_playlist_name = input("What is your playlist name: ")
playlist = sp.user_playlist_create(user_id, new_playlist_name, public=True)
new_playlist_id = playlist["id"]

# Search for each song by name and add it to the new playlist
track_ids = []
for i in range(len(song_names)):
    print(f"Searching for: {song_names[i][0]}")  # Debug: Print each search query
    query = f"{song_names[i][0]} {song_names[i][1]}"
    results = sp.search(q=query, type="track", limit=1)
    if results["tracks"]["items"]:  # Check if any results are returned
        track_id = results["tracks"]["items"][0]["id"]
        track_ids.append(track_id)
        print(f"Found and added song: {song_names[i][0]}")
    else:
        print(f"Song not found on Spotify: {song_names[i][0]}")

# Check if any tracks were found before attempting to add to playlist
if track_ids:
    sp.playlist_add_items(new_playlist_id, track_ids)
    print("All found songs added to playlist successfully!")
else:
    print("No songs were found to add to the playlist.")

# Construct the playlist URL and open it in the browser
playlist_url = f"https://open.spotify.com/playlist/{new_playlist_id}"
print(f"Playlist created successfully! You can view it here: {playlist_url}")
webbrowser.open(playlist_url)

print("Transferred playlist from text file to Spotify successfully!")
