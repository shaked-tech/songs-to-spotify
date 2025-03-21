import os
import sys
from pathlib import Path
import logging as log
import fire

# Add parent directory to Python path before any local imports
sys.path.insert(1, str(Path(__file__).parent.parent))

from spotify import Spotify, SpotifyError
from youtube import Youtube, YouTubeError


def setup_logging() -> None:
    """Configure logging based on environment variable"""
    log_level = os.environ.get("LOGLEVEL", "INFO").upper()
    log.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class PlaylistMigrator:
    """CLI tool for migrating playlists from YouTube to Spotify"""

    def migrate(self, youtube_secrets: str, youtube_playlist: str, spotify_user: str, spotify_token: str) -> None:
        """Migrate a YouTube playlist to Spotify

        Args:
            youtube_secrets: Path to YouTube client secrets file
            youtube_playlist: YouTube playlist ID to migrate
            spotify_user: Spotify user ID
            spotify_token: Spotify API token
        """
        setup_logging()

        try:
            # Initialize APIs
            youtube = Youtube(youtube_secrets)
            spotify = Spotify(spotify_user, spotify_token)

            # Get playlist details
            playlist_map = youtube.get_playlist_id_name(youtube_playlist)
            source_playlist_id = list(playlist_map.keys())[0]
            source_playlist_name = playlist_map.get(source_playlist_id)

            if not source_playlist_name:
                log.error(f"Could not find playlist name for ID: {youtube_playlist}")
                sys.exit(1)

            # Get songs and create Spotify playlist
            log.info(f"Getting songs from YouTube playlist: {source_playlist_name}")
            songs_list = youtube.get_songs_by_playlist_id(source_playlist_id)

            if not songs_list:
                log.warning("No songs found in the YouTube playlist")
                sys.exit(1)

            log.info(f"Creating playlist with {len(songs_list)} songs")
            spotify.tracks_to_spotify_playlist(
                playlist_id="", playlist_name=source_playlist_name, tracks_list=songs_list
            )
            log.info(f"Successfully migrated playlist: {source_playlist_name}")

        except (YouTubeError, SpotifyError) as e:
            log.error(f"Failed to migrate playlist: {str(e)}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
            sys.exit(1)


def main():
    """Main entry point"""
    fire.Fire(PlaylistMigrator)


if __name__ == "__main__":
    main()
