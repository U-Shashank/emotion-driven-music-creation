from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image
import numpy as np

from app.config import settings

class FrameProcessor:
    """Process video frames"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.frame_count = 0
    
    def save_frame(self, image: Image.Image) -> Optional[str]:
        """Save frame to disk if enabled"""
        if not settings.SAVE_FRAMES:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{self.client_id}_{timestamp}.jpg"
        filepath = settings.STORAGE_DIR / filename
        
        image.save(filepath, 'JPEG', quality=90)
        return filename
    
    def preprocess_frame(self, image: np.ndarray) -> np.ndarray:
        """Preprocess frame for model input"""
        # Add any preprocessing needed for your model
        # e.g., resize, normalize, etc.
        return image