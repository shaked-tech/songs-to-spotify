import logging as log
from dataclasses import dataclass
from os import path
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@dataclass
class PlaylistItem:
    """Data class for YouTube playlist items"""

    id: str
    title: str


class YouTubeError(Exception):
    """Custom exception for YouTube API errors"""

    pass


class Youtube:
    """Class to handle YouTube API operations"""

    def __init__(self, client_secrets_file: str) -> None:
        """Initialize YouTube client

        Args:
            client_secrets_file (str): Path to the client secrets file

        Raises:
            YouTubeError: If authentication fails
            ValueError: If client_secrets_file is empty or doesn't exist
        """
        if not client_secrets_file or not path.exists(client_secrets_file):
            raise ValueError("Valid client_secrets_file is required")

        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        api_service_name = "youtube"
        api_version = "v3"

        try:
            credentials = self._get_credentials(client_secrets_file, SCOPES)
            self.youtube_api = build(api_service_name, api_version, credentials=credentials)
            log.info("Initiated Youtube API successfully")
        except Exception as e:
            log.error(f"Failed to initialize YouTube API: {str(e)}")
            raise YouTubeError(f"YouTube API initialization failed: {str(e)}")

    def _get_credentials(self, client_secrets_file: str, scopes: List[str]) -> Credentials:
        """Get or refresh credentials for YouTube API

        Args:
            client_secrets_file (str): Path to the client secrets file
            scopes (List[str]): List of required API scopes

        Returns:
            Credentials: Valid credentials object

        Raises:
            YouTubeError: If authentication fails
        """
        credentials = None

        try:
            if path.exists("token.json"):
                credentials = Credentials.from_authorized_user_file("token.json", scopes)

            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    log.debug("Refreshing token")
                    credentials.refresh(Request())
                else:
                    log.debug("Creating new token file")
                    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
                    credentials = flow.run_local_server(port=0)

                with open("token.json", "w") as token:
                    token.write(credentials.to_json())

            return credentials
        except Exception as e:
            log.error(f"Authentication failed: {str(e)}")
            raise YouTubeError(f"Failed to authenticate: {str(e)}")

    def get_playlists_ids(self) -> List[str]:
        """Get all playlist IDs for the authenticated user

        Returns:
            List[str]: List of playlist IDs

        Raises:
            YouTubeError: If API request fails
        """
        try:
            response = (
                self.youtube_api.playlists().list(part="snippet,contentDetails", maxResults=50, mine=True).execute()
            )

            ids_list = [item["id"] for item in response.get("items", [])]
            log.info(f"Found {len(ids_list)} playlists")
            return ids_list
        except HttpError as e:
            log.error(f"Failed to get playlists: {str(e)}")
            raise YouTubeError(f"Failed to get playlists: {str(e)}")

    def get_playlist_id_name(self, id: str) -> Dict[str, str]:
        """Get playlist name by its ID

        Args:
            id (str): YouTube playlist ID

        Returns:
            Dict[str, str]: Dictionary mapping playlist ID to name

        Raises:
            YouTubeError: If API request fails or playlist not found
        """
        try:
            response = self.youtube_api.playlists().list(part="snippet,contentDetails", maxResults=1, id=id).execute()

            items = response.get("items", [])
            if not items:
                raise YouTubeError(f"Playlist {id} not found")
            if len(items) > 1:
                raise YouTubeError(f"Multiple playlists found for ID {id}")

            playlist_name = items[0]["snippet"]["title"]
            log.debug(f"{id}: {playlist_name}")
            return {id: playlist_name}
        except HttpError as e:
            log.error(f"Failed to get playlist {id}: {str(e)}")
            raise YouTubeError(f"Failed to get playlist {id}: {str(e)}")

    def get_songs_by_playlist_id(self, id: str) -> List[str]:
        """Get all song titles from a playlist

        Args:
            id (str): YouTube playlist ID

        Returns:
            List[str]: List of song titles

        Raises:
            YouTubeError: If API request fails
        """
        try:
            items = []
            next_page_token = None

            while True:
                response = (
                    self.youtube_api.playlistItems()
                    .list(
                        part="snippet,contentDetails",
                        maxResults=50,  # Increased from 5/25 to 50 for efficiency
                        playlistId=id,
                        pageToken=next_page_token,
                    )
                    .execute()
                )

                if not response.get("items"):
                    if not items:  # If this is the first request and no items
                        log.warning("No items found in playlist")
                        return []
                    break

                items.extend(response["items"])
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            log.debug(f"Found {len(items)} items for playlist {id}")
            return [item["snippet"]["title"] for item in items]
        except HttpError as e:
            log.error(f"Failed to get songs from playlist {id}: {str(e)}")
            raise YouTubeError(f"Failed to get songs from playlist {id}: {str(e)}")
