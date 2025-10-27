# """Mood/Emotion detection model"""
# import numpy as np
# from typing import Dict, Optional
# from app.config import settings

# class MoodDetector:
#     """Detect mood/emotion from facial images"""
    
#     def __init__(self):
#         self.model_type = settings.MODEL_TYPE
#         self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
#         self.total_detections = 0
        
#         print(f"🔧 Initializing {self.model_type} model...")
        
#         if self.model_type == "deepface":
#             self._init_deepface()
#         else:
#             print("⚠️  Using mock detector - implement your custom model!")
    
#     def _init_deepface(self):
#         """Initialize DeepFace model"""
#         try:
#             from deepface import DeepFace
#             self.deepface = DeepFace
#             print("✅ DeepFace model loaded")
#         except ImportError:
#             print("❌ DeepFace not installed. Run: uv add deepface")
#             self.deepface = None
    
#     def detect_mood(self, image: np.ndarray) -> Optional[Dict]:
#         """
#         Detect mood from image
        
#         Args:
#             image: numpy array of image (RGB)
            
#         Returns:
#             Dict with mood detection results
#         """
#         try:
#             if self.model_type == "deepface" and self.deepface:
#                 result = self.deepface.analyze(
#                     img_path=image,
#                     actions=['emotion'],
#                     enforce_detection=False,
#                     silent=True
#                 )
                
#                 # DeepFace returns list, get first result
#                 if isinstance(result, list):
#                     result = result[0]
                
#                 emotions = result.get('emotion', {})
#                 dominant_emotion = result.get('dominant_emotion', 'neutral')
#                 confidence = emotions.get(dominant_emotion, 0) / 100.0
                
#                 self.total_detections += 1
                
#                 return {
#                     "success": True,
#                     "dominant_emotion": dominant_emotion,
#                     "confidence": confidence,
#                     "emotions": emotions
#                 }
#             else:
#                 # Mock detection for testing
#                 import random
#                 moods = ["happy", "sad", "neutral", "angry", "surprise"]
#                 mood = random.choice(moods)
                
#                 self.total_detections += 1
                
#                 return {
#                     "success": True,
#                     "dominant_emotion": mood,
#                     "confidence": random.uniform(0.7, 0.95),
#                     "emotions": {m: random.uniform(0, 100) for m in moods}
#                 }
                
#         except Exception as e:
#             print(f"❌ Mood detection error: {e}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }

"""Mood/Emotion detection model"""
import numpy as np
import torch
import cv2
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
from typing import Dict, Optional
from pathlib import Path
from app.config import settings


class MoodDetector:
    """Detect mood/emotion from facial images using Vision Transformer"""
    
    def __init__(self):
        self.model_type = settings.MODEL_TYPE
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.total_detections = 0
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Emotion classes (matching your training)
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        print(f"🔧 Initializing {self.model_type} model on {self.device}...")
        
        if self.model_type == "custom":
            self._init_custom_model()
        elif self.model_type == "deepface":
            self._init_deepface()
        else:
            print("⚠️ Using mock detector")
    
    def _init_custom_model(self):
        """Initialize custom Vision Transformer model"""
        try:
            model_path = Path("best_model.pth")
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)
            print(f"📦 Loading checkpoint...")
            
            # Initialize ViT model architecture
            self.model = ViTForImageClassification.from_pretrained(
                'google/vit-base-patch16-224',
                num_labels=7,
                ignore_mismatched_sizes=True
            )
            
            # Load trained weights
            if isinstance(checkpoint, dict):
                if 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                    print(f"📊 Epoch: {checkpoint.get('epoch', 'N/A')}")
                    print(f"📊 Val Accuracy: {checkpoint.get('val_accuracy', 'N/A'):.2%}")
                    print(f"📊 Val Loss: {checkpoint.get('val_loss', 'N/A'):.4f}")
                elif 'state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
            else:
                self.model.load_state_dict(checkpoint)
            
            self.model.to(self.device)
            self.model.eval()
            
            # Initialize image processor (handles preprocessing automatically)
            self.processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
            
            # Classical CV enhancement flags (from your config)
            self.use_clahe = getattr(settings, 'USE_CLAHE', True)
            self.use_sharpening = getattr(settings, 'USE_SHARPENING', True)
            
            print(f"✅ Vision Transformer loaded successfully")
            print(f"🎯 Emotions: {', '.join(self.emotion_labels)}")
            print(f"🔧 CLAHE: {self.use_clahe}, Sharpening: {self.use_sharpening}")
            
        except Exception as e:
            print(f"❌ Failed to load custom model: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
    
    def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE for contrast enhancement (Lab 1-2)"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge and convert back
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    
    def _apply_sharpening(self, image: np.ndarray) -> np.ndarray:
        """Apply unsharp masking for feature enhancement (Lab 5)"""
        gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
        sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)
    
    def _preprocess_image(self, image: np.ndarray) -> Dict:
        """Preprocess image with classical CV techniques + ViT processor"""
        # Ensure uint8 format
        if image.dtype == np.float32 or image.dtype == np.float64:
            image = (image * 255).astype(np.uint8)
        
        # Apply classical CV enhancements
        if self.use_clahe:
            image = self._apply_clahe(image)
        
        if self.use_sharpening:
            image = self._apply_sharpening(image)
        
        # Convert to PIL for ViT processor
        pil_image = Image.fromarray(image)
        
        # Use ViT processor (handles resizing, normalization, etc.)
        inputs = self.processor(images=pil_image, return_tensors="pt")
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        return inputs
    
    def detect_mood(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect mood from image
        
        Args:
            image: numpy array of image (RGB)
        
        Returns:
            Dict with mood detection results
        """
        try:
            if self.model_type == "custom" and self.model is not None:
                # Preprocess image
                inputs = self._preprocess_image(image)
                
                # Run inference
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    probabilities = torch.nn.functional.softmax(logits, dim=-1)
                    confidence, predicted = torch.max(probabilities, 1)
                
                # Get emotion probabilities for all classes
                probs = probabilities[0].cpu().numpy()
                emotions = {label: float(prob * 100) 
                           for label, prob in zip(self.emotion_labels, probs)}
                
                dominant_emotion = self.emotion_labels[predicted.item()]
                confidence_score = float(confidence.item())
                
                self.total_detections += 1
                
                return {
                    "success": True,
                    "dominant_emotion": dominant_emotion,
                    "confidence": confidence_score,
                    "emotions": emotions,
                    "model_type": "ViT-base",
                    "meets_threshold": confidence_score >= self.confidence_threshold
                }
            
            elif self.model_type == "deepface" and self.deepface:
                result = self.deepface.analyze(
                    img_path=image,
                    actions=['emotion'],
                    enforce_detection=False,
                    silent=True
                )
                
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
                    "emotions": emotions,
                    "model_type": "deepface"
                }
            
            else:
                # Mock detection for testing
                import random
                mood = random.choice(self.emotion_labels)
                
                self.total_detections += 1
                
                return {
                    "success": True,
                    "dominant_emotion": mood,
                    "confidence": random.uniform(0.7, 0.95),
                    "emotions": {m: random.uniform(0, 100) for m in self.emotion_labels},
                    "model_type": "mock"
                }
        
        except Exception as e:
            print(f"❌ Mood detection error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _init_deepface(self):
        """Initialize DeepFace model"""
        try:
            from deepface import DeepFace
            self.deepface = DeepFace
            print("✅ DeepFace model loaded")
        except ImportError:
            print("❌ DeepFace not installed. Run: uv add deepface")
            self.deepface = None
    
    def get_stats(self) -> Dict:
        """Get detector statistics"""
        return {
            "total_detections": self.total_detections,
            "model_type": self.model_type,
            "device": str(self.device),
            "emotion_labels": self.emotion_labels,
            "num_classes": len(self.emotion_labels)
        }