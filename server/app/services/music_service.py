"""Music recommendation service"""
import json
import random
from typing import Dict, Optional
from pathlib import Path

from app.config import settings

class MusicService:
    """Handle music recommendations based on mood"""
    
    def __init__(self):
        self.use_spotify = settings.USE_SPOTIFY
        self.songs_db = self._load_songs_database()
        
        if self.use_spotify:
            self._init_spotify()
    
    def _load_songs_database(self) -> Dict:
        """Load local songs database"""
        db_path = settings.DATA_DIR / "songs.json"
        
        # Create default database if doesn't exist
        if not db_path.exists():
            default_db = {
                "happy": [
                    {"title": "Happy", "artist": "Pharrell Williams", "url": "spotify:track:..."},
                    {"title": "Good Vibrations", "artist": "The Beach Boys", "url": "spotify:track:..."},
                    {"title": "Walking on Sunshine", "artist": "Katrina and the Waves", "url": "spotify:track:..."}
                ],
                "sad": [
                    {"title": "Someone Like You", "artist": "Adele", "url": "spotify:track:..."},
                    {"title": "The Night We Met", "artist": "Lord Huron", "url": "spotify:track:..."},
                    {"title": "Skinny Love", "artist": "Bon Iver", "url": "spotify:track:..."}
                ],
                "angry": [
                    {"title": "Break Stuff", "artist": "Limp Bizkit", "url": "spotify:track:..."},
                    {"title": "Killing in the Name", "artist": "Rage Against the Machine", "url": "spotify:track:..."},
                ],
                "neutral": [
                    {"title": "Weightless", "artist": "Marconi Union", "url": "spotify:track:..."},
                    {"title": "Clair de Lune", "artist": "Debussy", "url": "spotify:track:..."},
                ],
                "surprise": [
                    {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "url": "spotify:track:..."},
                ],
                "fear": [
                    {"title": "Breathe Me", "artist": "Sia", "url": "spotify:track:..."},
                ],
                "disgust": [
                    {"title": "Toxic", "artist": "Britney Spears", "url": "spotify:track:..."},
                ]
            }
            
            with open(db_path, 'w') as f:
                json.dump(default_db, f, indent=2)
            
            return default_db
        
        with open(db_path, 'r') as f:
            return json.load(f)
    
    def _init_spotify(self):
        """Initialize Spotify client"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            
            auth_manager = SpotifyClientCredentials(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET
            )
            self.spotify = spotipy.Spotify(auth_manager=auth_manager)
            print("✅ Spotify client initialized")
        except Exception as e:
            print(f"⚠️  Spotify initialization failed: {e}")
            self.spotify = None
    
    def get_song_for_mood(self, mood: str) -> Optional[Dict]:
        """Get song recommendation for given mood"""
        mood = mood.lower()
        
        # Get songs for this mood
        songs = self.songs_db.get(mood, self.songs_db.get("neutral", []))
        
        if not songs:
            return None
        
        # Return random song from mood category
        song = random.choice(songs)
        
        return {
            "title": song["title"],
            "artist": song["artist"],
            "url": song.get("url", ""),
            "mood": mood
        }
    
    def search_spotify(self, mood: str, query: str) -> Optional[Dict]:
        """Search Spotify for mood-based songs"""
        if not self.use_spotify or not self.spotify:
            return None
        
        try:
            results = self.spotify.search(q=query, type='track', limit=1)
            tracks = results['tracks']['items']
            
            if tracks:
                track = tracks[0]
                return {
                    "title": track['name'],
                    "artist": track['artists'][0]['name'],
                    "url": track['external_urls']['spotify'],
                    "uri": track['uri'],
                    "mood": mood
                }
        except Exception as e:
            print(f"❌ Spotify search error: {e}")
        
        return None