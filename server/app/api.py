"""REST API endpoints"""
from fastapi import APIRouter, Request
from typing import Dict

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Mood Tracker API is running"
    }

@router.get("/stats")
async def get_stats(request: Request) -> Dict:
    """Get server statistics"""
    # Access mood detector from app state
    mood_detector = request.app.state.mood_detector
    
    return {
        "total_detections": mood_detector.total_detections,
        "model_type": mood_detector.model_type,
    }

@router.get("/moods")
async def get_available_moods() -> Dict:
    """Get list of detectable moods"""
    return {
        "moods": [
            "happy", "sad", "angry", "surprise", 
            "fear", "disgust", "neutral"
        ]
    }