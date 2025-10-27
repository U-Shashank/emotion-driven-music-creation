"""Configuration settings"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage" / "frames"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Model settings
    MODEL_TYPE: str = os.getenv("MODEL_TYPE", "custom")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
    DETECTION_INTERVAL: int = int(os.getenv("DETECTION_INTERVAL", "30"))
    
    # Music settings
    USE_SPOTIFY: bool = os.getenv("USE_SPOTIFY", "false").lower() == "true"
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    # Storage
    SAVE_FRAMES: bool = os.getenv("SAVE_FRAMES", "false").lower() == "true"

    # Image Enhancement
    USE_CLAHE: bool = os.getenv("USE_CLAHE", "false").lower() == "true"
    USE_SHARPENING: bool = os.getenv("USE_SHARPENING", "false").lower() == "true"
    
    def __init__(self):
        """Initialize settings and create directories"""
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()