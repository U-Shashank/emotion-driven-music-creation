"""Mood/Emotion detection model"""
import numpy as np
from typing import Dict, Optional
from app.config import settings

class MoodDetector:
    """Detect mood/emotion from facial images"""
    
    def __init__(self):
        self.model_type = settings.MODEL_TYPE
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.total_detections = 0
        
        print(f"🔧 Initializing {self.model_type} model...")
        
        if self.model_type == "deepface":
            self._init_deepface()
        else:
            print("⚠️  Using mock detector - implement your custom model!")
    
    def _init_deepface(self):
        """Initialize DeepFace model"""
        try:
            from deepface import DeepFace
            self.deepface = DeepFace
            print("✅ DeepFace model loaded")
        except ImportError:
            print("❌ DeepFace not installed. Run: uv add deepface")
            self.deepface = None
    
    def detect_mood(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect mood from image
        
        Args:
            image: numpy array of image (RGB)
            
        Returns:
            Dict with mood detection results
        """
        try:
            if self.model_type == "deepface" and self.deepface:
                result = self.deepface.analyze(
                    img_path=image,
                    actions=['emotion'],
                    enforce_detection=False,
                    silent=True
                )
                
                # DeepFace returns list, get first result
                if isinstance(result, list):
                    result = result[0]
                
                emotions = result.get('emotion', {})
                dominant_emotion = result.get('dominant_emotion', 'neutral')
                confidence = emotions.get(dominant_emotion, 0) / 100.0
                
                self.total_detections += 1
                
                return {
                    "success": True,
                    "dominant_emotion": dominant_emotion,
                    "confidence": confidence,
                    "emotions": emotions
                }
            else:
                # Mock detection for testing
                import random
                moods = ["happy", "sad", "neutral", "angry", "surprise"]
                mood = random.choice(moods)
                
                self.total_detections += 1
                
                return {
                    "success": True,
                    "dominant_emotion": mood,
                    "confidence": random.uniform(0.7, 0.95),
                    "emotions": {m: random.uniform(0, 100) for m in moods}
                }
                
        except Exception as e:
            print(f"❌ Mood detection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }