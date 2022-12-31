from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from os import path
import logging as log

class Youtube:
    def __init__(self, client_secrets_file):
        # Using credentials file:
        # If modifying these scopes, delete the file token.json.
        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        api_service_name = "youtube"
        api_version = "v3"
        credentials = None
        
        if path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                log.debug("Refreshing token")
                credentials.refresh(Request())
            else:
                log.debug("Creating token new file")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())

        self.youtube_api = build(
            api_service_name, api_version, credentials=credentials
        )
        log.info(f"Initiated Youtube api succesfully")

    def get_playlists_ids(self) -> list:
        response = self.youtube_api.playlists().list(
            part="snippet,contentDetails",
            maxResults=50,
            mine=True
        ).execute()

        # return a list of id of all playlists of user
        ids_list = [item['id'] for item in response.get('items')]
        log.info(f"Found {len(ids_list)} playlists")
        return ids_list

    def get_playlist_id_title(self, playlist_id) -> dict:
        response = self.youtube_api.playlists().list(
            part="snippet,contentDetails",
            maxResults=1,
            id=playlist_id
        ).execute()

        if len(response.get('items')) > 1:
            raise

        log.debug(f"{playlist_id}: {response.get('items')[0]['snippet']['title']}")
        playlist_map = {playlist_id: response.get('items')[0]['snippet']['title']}
        return playlist_map

    def get_video_title_by_id(self, video_id):
        """Get string of title of video"""
        response = self.youtube_api.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        return response["items"][0]["snippet"]["title"]

    def get_playlist_title_by_id(self, playlist_id):
        """Get string playlist title of playlist"""
        response = self.youtube_api.playlists().list(
            part="snippet",
            id=playlist_id,
            maxResults=1,
        ).execute()

        return response["items"][0]["snippet"]["title"]

    def get_videos_by_playlist_id(self, playlist_id) -> list:
        """Get a list containing videos ids of playlist"""
        response = self.youtube_api.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            playlistId=playlist_id
        ).execute()

        if 1 > response.get('pageInfo').get('totalResults'):
            print("No items found in playlist")
            return []
        else:
            items = response.get('items')
            nextPageToken = response.get('nextPageToken')
            while nextPageToken:
                response_next_page = self.youtube_api.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=50,
                    playlistId=playlist_id,
                    pageToken=nextPageToken
                ).execute()
                items.extend(response_next_page.get('items'))
                nextPageToken = response_next_page.get('nextPageToken')
            log.debug(f"found {len(items)} items for playlist {playlist_id}")

            songs_list = [item["snippet"]["resourceId"]["videoId"] for item in items]
            return songs_list

    def get_all_video_ids_in_playlist(self, playlist_id):
        response = self.youtube_api.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
        ).execute()

        video_ids = [response["snippet"]["resourceId"]["videoId"] for response in response["items"]]
        return video_ids

    def rate_video_by_id(self, video_id, rate) -> None:
        """Unrate video"""
        log.debug(f"rating {video_id} with {rate}")
        try:
            self.youtube_api.videos().rate(
                id=video_id,
                rating=rate
            ).execute()
        except HttpError as e:
            video_name = self.get_video_title_by_id(video_id)
            log.WARNING(f"could not rate {video_name}, {e}")

    def create_playlist(self, playlist_title, playlist_description="", tags=[], defaultLanguage="en", privacyStatus="private"):
        response = self.youtube_api.playlists().insert(
            part="snippet,status",
            body = {
                "snippet": {
                    "title": playlist_title,
                    "description": playlist_description,
                    "tags": tags,
                    "defaultLanguage": defaultLanguage
                },
                "status": {
                    "privacyStatus": privacyStatus
                }
            }
        ).execute()

        return(response["id"])

    def rate_all_videos_in_playlist(self, playlist_id: str, rate: str):
        """Rate all videos in a playlist with one of: ['like','dislike','none']"""
        # method = {'like':self.like_video_by_id(id),'dislike':self.dislike_video_by_id(id),'none':self.unrate_video_by_id(id)}
        playlist_name = self.get_playlist_title_by_id(playlist_id)
        ids = self.get_all_video_ids_in_playlist(playlist_id)

        log.info(f"Rating songs in playlist '{playlist_name}' with {rate}")
        for id in ids:
            self.rate_video_by_id(id, rate)

# TODO:
    # def upload_videos_to_playlist(self, playlist_id, videos_uris):
    # def videos_to_youtube_playlist(self, playlist_title, videos_list):