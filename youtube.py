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
        
    def get_playlist_id_name(self, id) -> dict:
        response = self.youtube_api.playlists().list(
            part="snippet,contentDetails",
            maxResults=1,
            id=id
        ).execute()
        if len(response.get('items')) > 1:
            raise

        log.debug(f"{id}: {response.get('items')[0]['snippet']['title']}")
        playlist_map = {id: response.get('items')[0]['snippet']['title']}
        return playlist_map

    def get_songs_by_playlist_id(self, id):
        response = self.youtube_api.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=5,
            playlistId=id
        ).execute()
        if 1 > response.get('pageInfo').get('totalResults'):
            print("No items found in playlist")
            return
        else:
            items = response.get('items')
            nextPageToken = response.get('nextPageToken')
            while nextPageToken:
                response_next_page = self.youtube_api.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=25,
                    playlistId=id,
                    pageToken=nextPageToken
                ).execute()
                items.extend(response_next_page.get('items'))
                nextPageToken = response_next_page.get('nextPageToken')
            log.debug(f"found {len(items)} items for playlist {id}")

            songs_list = [item['snippet']['title'] for item in items]
            return songs_list
