from os import environ

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')

from youtube import Youtube
from spotify import Spotify

if __name__ == '__main__':
    LOGLEVEL = environ.get('LOGLEVEL', 'INFO').upper()

    youtube_client_secrets_file_path = ""
    youtube_playlist_id = ""
    spotify_user_id = ""
    spotify_token = ""

    youtube = Youtube(youtube_client_secrets_file_path)
    spotify = Spotify(spotify_user_id, spotify_token)

    playlist_map = youtube.get_playlist_id_name(youtube_playlist_id)

    source_playlist_id = list(playlist_map.keys())[0]
    source_playlist_name = playlist_map.get(source_playlist_id)

    songs_list = youtube.get_songs_by_playlist_id(source_playlist_id)
    spotify.tracks_to_spotify_playlist(source_playlist_name, songs_list)
