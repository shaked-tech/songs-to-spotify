import unittest
from spotify import Spotify

global user_id
global token
global test_playlist_id
global spotify

user_id = ""
token = ""
test_playlist_id = ""
spotify = Spotify(user_id, token)

class TestSum(unittest.TestCase):
    def test_get_all_tracks_ids_in_playlist(self):
        """
        Test get_all_tracks_ids_in_playlist works
        """
        songs_in_testing_playlist = len(spotify.get_all_tracks_ids_in_playlist(test_playlist_id))
        self.assertEqual(songs_in_testing_playlist, 12)

if __name__ == '__main__':
    unittest.main()
