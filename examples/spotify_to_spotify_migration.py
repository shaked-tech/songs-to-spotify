import logging as log
import sys
from os import environ
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(1, str(Path(__file__).parent.parent))

from spotify import Spotify, SpotifyError
import fire


def setup_logging() -> None:
    """Configure logging based on environment variable"""
    log_level = environ.get("LOGLEVEL", "INFO").upper()
    log.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class SpotifyMigrator:
    """CLI tool for migrating playlists between Spotify accounts"""

    def migrate(self,
                source_user: str,
                source_token: str,
                target_user: str,
                target_token: str,
                source_playlist_id: str,
                target_playlist_id: str = '') -> None:
        """Migrate a playlist from one Spotify account to another

        Args:
            source_user: Source Spotify user ID
            source_token: Source Spotify API token
            target_user: Target Spotify user ID
            target_token: Target Spotify API token
            playlist_id: ID of the playlist to migrate
        """
        setup_logging()

        try:
            # Initialize Spotify clients for both accounts
            source_spotify = Spotify(source_user, source_token)
            target_spotify = Spotify(target_user, target_token)

            # Get playlist details from source account
            playlist_name = source_spotify.get_playlist_name(source_playlist_id)
            if not playlist_name:
                log.error(f"Could not find playlist with ID: {source_playlist_id}")
                sys.exit(1)

            # Get tracks from source playlist
            log.info(f"Getting tracks from playlist: {playlist_name}")
            tracks_list = source_spotify.get_tracks_from_playlist(source_playlist_id)
            if not tracks_list:
                log.warning("No tracks found in the playlist")
                sys.exit(1)

            # Create playlist in target account and add tracks
            log.info(f"Creating playlist with {len(tracks_list)} tracks in target account")
            target_spotify.tracks_to_spotify_playlist(playlist_id=target_playlist_id,
                                                      playlist_name=playlist_name,
                                                      tracks_list=tracks_list)
            log.info(f"Successfully migrated playlist: {playlist_name}")

        except SpotifyError as e:
            log.error(f"Failed to migrate playlist: {str(e)}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
            sys.exit(1)


def main():
    """Main entry point"""
    fire.Fire(SpotifyMigrator)


if __name__ == "__main__":
    main()
