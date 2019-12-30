import spotipy
import pandas as pd

def get_playlists(token):
    ''' Returns a list of all the playlists associated with an authenticated user '''
    sp = spotipy.Spotify(auth=token)
    playlists = sp.current_user_playlists()['items']
    return playlists

def get_playlist_data(token, playlist_id):
    ''' Collect all the data from a playlist and convert into a pandas dataframe '''
    # Initialize all necessary data lists
    ids = []
    artists = []
    dates_added = []
    counts = []
    song_counts  = {}

    sp = spotipy.Spotify(auth=token) # Setup user
    playlist = sp.user_playlist(sp.current_user()['id'], playlist_id=playlist_id, fields='name,tracks') # Get the requested playlist
    tracks = playlist['tracks']
    collect_info(tracks['items'], ids, artists, counts, dates_added, song_counts)
    while tracks['next']: # While there are still pages of songs to collect
        tracks = sp.next(tracks)
        collect_info(tracks['items'], ids, artists, counts, dates_added, song_counts)
    data = {'id':ids, 'artist':artists, 'date_added':dates_added, 'count':counts}
    df = pd.DataFrame(data) # Create dataframe
    df['date_added'] = df['date_added'].astype('datetime64[ns]').dt.normalize() # Convert all dates into panda dates
    return df

def collect_info(tracks, ids, artists, counts, dates_added, song_counts):
    ''' Collect necessary info from each track '''
    for track in tracks:
        artist = track['track']['artists'][0]
        dates_added.append(track['added_at'])
        if (artist['id'] in ids):
            song_counts[artist['id']]+=1 # Increment number of songs associated with artist
        else:
            song_counts[artist['id']] = 0 # Create new artist
        ids.append(artist['id'])
        artists.append(artist['name'])
        counts.append(song_counts[artist['id']])
