import json
import logging as log
from dataclasses import dataclass
from time import sleep
from typing import Dict, List, Optional
import re

import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class Track:
    name: str
    uri: str
    artist: str


class SpotifyError(Exception):
    """Custom exception for Spotify API errors"""

    pass


class Spotify:
    """Class to handle Spotify API operations"""

    def __init__(self, user_id: str, token: str) -> None:
        """Initialize Spotify client

        Args:
            user_id (str): Spotify user ID
            token (str): Spotify API token

        Raises:
            ValueError: If user_id or token is empty
        """
        if not user_id or not token:
            raise ValueError("user_id and token are required")
        self.user_id = user_id
        self.token = token
        self.not_found_list: List[str] = []
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> Dict:
        """Make an HTTP request to Spotify API with retry logic

        Args:
            method (str): HTTP method (get, post, put)
            url (str): API endpoint URL
            data (Optional[Dict]): Request body for POST/PUT requests

        Returns:
            Dict: JSON response from the API

        Raises:
            SpotifyError: If the API request fails
        """
        try:
            response = requests.request(
                method=method, url=url, headers=self.headers, data=json.dumps(data) if data else None
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except RequestException as e:
            log.error(f"Spotify API error: {str(e)}")
            raise SpotifyError(f"Failed to {method} {url}: {str(e)}")

    def get_total_liked_tracks(self) -> int:
        """Get total number of liked tracks

        Returns:
            int: Total number of liked tracks
        """
        tracks_url = "https://api.spotify.com/v1/me/tracks?offset=0&limit=1"
        response = self._make_request("get", tracks_url)
        return response["total"]

    def get_all_user_playlists_ids(self) -> List[str]:
        """Get all user playlists IDs

        Returns:
            List[str]: List of playlist IDs
        """
        playlists_url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = self._make_request("get", playlists_url)
        return [item["id"] for item in response["items"]]

    def get_all_liked_tracks(self) -> List[str]:
        """Get all liked tracks IDs

        Returns:
            List[str]: List of track IDs
        """
        total_retrieved = 0
        ids = []
        total = self.get_total_liked_tracks()
        while total_retrieved < total:
            query = f"https://api.spotify.com/v1/me/tracks?offset={total_retrieved}&limit=50"
            response = self._make_request("get", query)
            for _, j in enumerate(response["items"]):
                ids.append(j["track"]["id"])
                total_retrieved += 1
        return ids

    def get_all_tracks_ids_in_playlist(self, playlist_id: str) -> List[str]:
        """Get all tracks IDs in a playlist

        Args:
            playlist_id (str): Spotify playlist ID

        Returns:
            List[str]: List of track IDs
        """
        ids = []
        get_playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100"
        response = self._make_request("get", get_playlist_url)
        while True:
            ids_temp = [item["track"]["id"] for item in response["items"]]
            ids.extend(ids_temp)
            if response["next"] is None:
                break
            next_playlist_url = response["next"]
            response = self._make_request("get", next_playlist_url)
        return ids

    def search_for_track_uri_by_name(self, track_name: str) -> Optional[str]:
        """Search for a track URI by its name

        Args:
            track_name (str): Track name

        Returns:
            Optional[str]: Track URI if found, None otherwise
        """
        limit = 2
        search_url = f"https://api.spotify.com/v1/search?q={track_name}&limit={limit}&type=track"
        response = self._make_request("get", search_url)
        if response["tracks"]["total"] == 0:
            return None
        track_list = response["tracks"]["items"][0]
        track_uri = track_list["uri"]
        track_name = track_list["name"]
        track_artist = track_list["artists"][0]["name"]
        log.info(f'Found "{track_name}" by {track_artist}')
        return track_uri

    def like_track_by_id(self, id: str) -> bool:
        """Like a track by its ID

        Args:
            id (str): Track ID

        Returns:
            bool: True if successful, False otherwise
        """
        like_track_url = f"https://api.spotify.com/v1/me/tracks?ids={id}"
        self._make_request("put", like_track_url)
        return True

    def like_all_tracks_in_playlist(self, playlist_id: str) -> bool:
        """Like all tracks in a playlist

        Args:
            playlist_id (str): Spotify playlist ID

        Returns:
            bool: True if successful, False otherwise
        """
        count = 0
        ids = self.get_tracks_from_playlist(playlist_id)
        for id in ids:
            self.like_track_by_id(id)
            log.info(".", end=" ", flush=True)
            count += 1
        log.info(f"Liked {count} Songs!")
        return True

    def create_playlist(self, playlist_name: str) -> str:
        """Create a new playlist

        Args:
            playlist_name (str): Playlist name

        Returns:
            str: Playlist ID
        """
        create_playlist_url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        log.info(f"Creating playlist '{playlist_name}':")
        request_body = {"name": playlist_name, "description": f"Python uploaded {playlist_name}", "public": False}
        response = self._make_request("post", create_playlist_url, request_body)
        log.info(f"Created playlist '{playlist_name}'")
        return response["id"]

    def upload_tracks_to_playlist(self, playlist_id: str, tracks_uris: List[str]) -> None:
        """Upload tracks to a playlist

        Args:
            playlist_id (str): Spotify playlist ID
            tracks_uris (List[str]): List of track URIs
        """
        upload_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        n = 100
        uris = [tracks_uris[i : i + n] for i in range(0, len(tracks_uris), n)]
        # log.debug(uris)
        for chunk in uris:
            request_body = {"uris": chunk}
            self._make_request("post", upload_url, request_body)

    def tracks_to_spotify_playlist(self, playlist_id: str, playlist_name: str, tracks_list: List[str]) -> None:
        """Create a playlist and add tracks to it

        Args:
            playlist_id (str): Spotify playlist ID
            playlist_name (str): Name for the new playlist, if both playlist_id and playlist_name are empty,
            a new playlist will not be created
            tracks_list (List[str]): List of track names to search and add
        """
        tracks_uris = []
        dots = ["", ".", "..", "...", "...."]

        try:
            if playlist_id == '' and playlist_name != '':
                playlist_id = self.create_playlist(playlist_name)

            for index, track_name in enumerate(tracks_list):
                print(f"Searching songs{dots[index % len(dots)]}    ", end="\r")
                log.debug(f"Searching for track: {track_name}")
                track_name_formated = re.sub(r'\([^)]*\)', '', track_name)
                name_parts = track_name_formated.split(' - ')
                if len(name_parts) > 1:
                    track_name_formated = name_parts[1] + ' ' + name_parts[0]
                    print(f"Reformatted track name: '{track_name_formated}'")
                track_uri = self.search_for_track_uri_by_name(track_name_formated)
                if track_uri:
                    tracks_uris.append(track_uri)
                else:
                    log.info(f'"{track_name}", Was not found')
                    self.not_found_list.append(track_name)

            if tracks_uris:
                self.upload_tracks_to_playlist(playlist_id, tracks_uris)
                log.info(f"Searching songs{dots[-1]}Done")
                sleep(1.1)

                log.info(
                    f"Added {len(tracks_uris)} songs to playlist: '{playlist_name}' \
                     (https://open.spotify.com/playlist/{playlist_id})"
                )
                if self.not_found_list:
                    log.warning(f"Could not find {len(self.not_found_list)} songs: {self.not_found_list}")
        except SpotifyError as e:
            log.error(f"Failed to create playlist: {str(e)}")
            raise

    def get_playlist_name(self, playlist_id: str) -> str:
        """Get the name of a playlist by its ID

        Args:
            playlist_id: Spotify playlist ID

        Returns:
            str: Name of the playlist
        """
        playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        response = self._make_request("get", playlist_url)
        return response["name"]

    def get_tracks_from_playlist(self, playlist_id: str) -> List[str]:
        """Get all track names from a playlist

        Args:
            playlist_id: Spotify playlist ID

        Returns:
            List[str]: List of track names in format "Artist - Song"
        """
        tracks = []
        offset = 0
        limit = 100

        while True:
            playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit={limit}"
            response = self._make_request("get", playlist_url)

            if not response["items"]:
                break

            for item in response["items"]:
                track = item["track"]
                artist = track["artists"][0]["name"]
                name = track["name"]
                tracks.append(f"{artist} - {name}")

            if len(response["items"]) < limit:
                break

            offset += limit

        return tracks
