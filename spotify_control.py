import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify developer credentials
# WARNING: These should be moved to environment variables for security
# Consider using: CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_client_id')
CLIENT_ID = "7e7ac65c8c4b442bbb78a7ecb55379b0"
CLIENT_SECRET = "915cd72b31834e9c95e9427b524c8fbf"
REDIRECT_URI = "http://127.0.0.1:5000/callback/"
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

class SpotifyController:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))

    def _get_active_device(self):
        """Returns the ID of the first active device."""
        devices = self.sp.devices()
        if devices['devices']:
            return devices['devices'][0]['id']
        return None

    def play_song(self, song_name):
        """Searches and plays a specific song by name."""
        results = self.sp.search(q=song_name, type="track", limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            device_id = self._get_active_device()
            if device_id:
                self.sp.start_playback(device_id=device_id, uris=[track_uri])
                return f"Playing {song_name} on Spotify."
            else:
                return "No active Spotify device found."
        else:
            return f"Song '{song_name}' not found."

    def pause(self):
        """Pauses current playback."""
        try:
            self.sp.pause_playback()
            return "Spotify playback paused."
        except:
            return "Unable to pause playback."

    def resume(self):
        """Resumes current playback."""
        try:
            self.sp.start_playback()
            return "Spotify playback resumed."
        except:
            return "Unable to resume playback."

    def next_track(self):
        """Skips to the next track."""
        try:
            self.sp.next_track()
            return "Skipped to next track."
        except:
            return "Unable to skip track."

    def previous_track(self):
        """Goes back to the previous track."""
        try:
            self.sp.previous_track()
            return "Playing previous track."
        except:
            return "Unable to go to previous track."

    def set_volume(self, volume_level):
        """Sets the playback volume (0–100)."""
        try:
            self.sp.volume(volume_percent=volume_level)
            return f"Spotify volume set to {volume_level}%."
        except:
            return "Unable to set volume."

    def shuffle(self, shuffle_state):
        """Enables or disables shuffle mode."""
        try:
            self.sp.shuffle(state=shuffle_state)
            return f"Shuffle {'enabled' if shuffle_state else 'disabled'}."
        except:
            return "Unable to change shuffle state."

    def repeat(self, repeat_state):
        """Sets repeat mode: 'track', 'context', or 'off'."""
        try:
            self.sp.repeat(state=repeat_state)
            return f"Repeat mode set to {repeat_state}."
        except:
            return "Unable to change repeat mode."

    def play_playlist(self, playlist_uri):
        """Plays a playlist by URI."""
        try:
            device_id = self._get_active_device()
            if device_id:
                self.sp.start_playback(device_id=device_id, context_uri=playlist_uri)
                return "Playing playlist."
            else:
                return "No active Spotify device found."
        except:
            return "Unable to play playlist."

    def current_playing(self):
        """Returns the current playing track."""
        try:
            track = self.sp.current_playback()
            if track and track['item']:
                name = track['item']['name']
                artist = track['item']['artists'][0]['name']
                return f"Currently playing: {name} by {artist}."
            else:
                return "Nothing is currently playing."
        except:
            return "Unable to get current track info."
