# Songs-To-Spotify
Hi there! <br>
Songs-to-spotify is a Python project used to automate actions in your spotify account.
The main feature currently available is the migration of playlists from Youtube to Spotify.

<br>

# Usage
In order to do so you will require permissions to authenticate with for each API provider.
### Examples

#### Migrate Single YouTube Playlist to Spotify:
To migrate a single YouTube playlist to Spotify, use the following command:

```bash
python3 examples/single_playlist_youtube_to_spotify.py migrate \
    --youtube-secrets=/path/to/client_secrets.json \
    --youtube-playlist=YOUTUBE_PLAYLIST_ID \
    --spotify-user=YOUR_SPOTIFY_USER_ID \
    --spotify-token=YOUR_SPOTIFY_TOKEN
```

Replace the following values:
- `/path/to/client_secrets.json`: Path to your YouTube API credentials file
- `YOUTUBE_PLAYLIST_ID`: ID of the YouTube playlist you want to migrate (found in the playlist URL)
- `YOUR_SPOTIFY_USER_ID`: Your Spotify user ID (from steps above)
- `YOUR_SPOTIFY_TOKEN`: Your Spotify API token (from steps above)

The script will create a new Spotify playlist with the same name as the YouTube playlist and copy all available songs.

#### Migrate Playlist Between Spotify Accounts:
To migrate a playlist from one Spotify account to another, use the following command:

```bash
python3 examples/spotify_to_spotify_migration.py migrate \
    --source-user=SOURCE_SPOTIFY_USER_ID \
    --source-token=SOURCE_SPOTIFY_TOKEN \
    --target-user=TARGET_SPOTIFY_USER_ID \
    --target-token=TARGET_SPOTIFY_TOKEN \
    --playlist-id=PLAYLIST_ID
```

Replace the following values:
- `SOURCE_SPOTIFY_USER_ID`: User ID of the source Spotify account
- `SOURCE_SPOTIFY_TOKEN`: API token for the source Spotify account
- `TARGET_SPOTIFY_USER_ID`: User ID of the target Spotify account
- `TARGET_SPOTIFY_TOKEN`: API token for the target Spotify account
- `PLAYLIST_ID`: ID of the playlist to migrate (found in the playlist URL)

The script will create a new playlist in the target account with the same name and songs as the source playlist.

## Spotify Permissions:
### 'spotify_user_id':
1. Getting user id: <br>
    a. Login to your spotify application or web, click icon on top right. <br>
    b. Click on 'Account'. <br>
    c. In opened page, under 'Account overview' copy 'Username' string and use it under 'spotify_user_id'.

### 'spotify_token':
1. Login into: https://developer.spotify.com/console/get-recommendations/
2. Getting token from Spotify:
    - At the bottom of the page click 'GET TOKEN'
    - Depending on the action you want to preform you will need to allow different permissions ('modify' permissions allow read+write):
        - 'playlist-read-private' - Read permissions for private playlists.
        - 'playlist-modify-private' - Write permissions for private playlists.
        - 'playlist-read-public' - Read permissions for public playlists.
        - 'playlist-modify-public' - Write permissions for public playlists.
        - 'user-library-read' - Read permissions for 'liked songs' playlist.
        - 'user-library-modify' - Write permissions for 'liked songs' playlist.

3. Copy token and use it under 'spotify_token'

## Youtube Permissions:
### 'youtube_playlist':
1. Get playlist ID:
    - Go to the YouTube playlist you want to migrate
    - Copy the playlist ID from the URL, starting with 'PL-...'

### Prerequisites:
##### Enable Youtube v3 API:
In your GCP project, allow access to Youtube api at: https://console.cloud.google.com/apis/library/youtube.googleapis.com <br>
If Youtube api is not yet enabled, Click 'Enable'.

### Access Credentials For Youtube API:
#### Choose one of the following:
##### 1) Credentials file access (Recommended):
- Go to: https://console.cloud.google.com/apis/

'create branding'

- Add tester's user mail address:
    - Press 'OAuth consent screen'
    - Under test users, add the email used to authenticate
- Create credentials file:
    - 'create credentials' --> 'OAuth client ID' --> select 'Desktop app' + enter name --> Create
    - Download credentials file
    - Update 'youtube_client_secrets_file_path' variable with the file path
- Add authorized user:
    - Under 'Test users', press 'ADD USERS'
    - Enter user email address


##### 2) User authorised access:
Ref: https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification?hl=en#submit-app-for-verification


### Learn about Youtube api access:
Ref: https://developers.google.com/people/quickstart/python
https://www.youtube.com/watch?v=E4lX2lnKsPM

<br>

## Support
Any issues, comments, suggestions or straight on complements are very welcome. <br>
Hope you enjoy and thanks in advance!

<br>

## License
The source code for the site is licensed under the MIT license, which you can find in the LICENSE file.
