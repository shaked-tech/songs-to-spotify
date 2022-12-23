# Spotify Permissions:
## 'spotify_user_id':
1. Login to Spotify
2. Getting user id:
    a. Login to your spotify application or web, click icon on top right
    b. Click on 'Account'
    c. In opened page, under 'Account overview' copy 'Username' string and use it under 'spotify_user_id'.
## 'spotify_token':
1. Login into: https://developer.spotify.com/console/get-recommendations/
2. Getting token from Spotify:
    - At the bottom of the page click 'GET TOKEN'
    - Depending on the action you want to preform you will need to allow differant permissions, ('modify' permissions allow read+write):
        - 'playlist-read-private' - Read permissions for private playlists.
        - 'playlist-modify-private' - Write permissions for private playlists.
        - 'playlist-read-public' - Read permissions for public playlists.
        - 'playlist-modify-public' - Write permissions for public playlists.
        - 'user-library-read' - Read permissions for 'liked songs' playlist.
        - 'user-library-modify' - Write permissions for 'liked songs' playlist.

3. Copy token and use it under 'spotify_token'

<br/>

# Youtube Permissions:
## Prerequisites:
#### Enable Youtube v3 API:
In your GCP project, allow access to Youtube api at: https://console.cloud.google.com/apis/library/youtube.googleapis.com

If Youtube api is not yet enabled, Click 'Enable'.

<br/>

## Access Credentials For Youtube API:
### 1) Choose one of the following:
#### Credentials file access (Recommended):
- Go to: https://console.cloud.google.com/apis/
- Add tester's user mail address:
    - Press 'OAuth consent screen'
    - Under test users, add the email used to authenticate 
- Create credentials file:
    - 'create credentials' --> 'OAuth client ID' --> select 'Desktop app' + enter name --> Create
    - Download credentials file
    - Update 'youtube_client_secrets_file_path' variable with the file path

#### 2) User authorised access:
Ref: https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification?hl=en#submit-app-for-verification


## Learn about Youtube api access: 
Ref: https://developers.google.com/people/quickstart/python
https://www.youtube.com/watch?v=E4lX2lnKsPM
