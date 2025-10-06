"""WebSocket handlers for real-time frame processing"""
import json
import asyncio
import time
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from PIL import Image
import io
import numpy as np

from app.services.frame_processor import FrameProcessor
from app.services.music_service import MusicService

router = APIRouter()

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.frame_processors: Dict[str, FrameProcessor] = {}
        self.last_detection_time: Dict[str, float] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.frame_processors[client_id] = FrameProcessor(client_id)
        self.last_detection_time[client_id] = 0
        print(f"✅ Client {client_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.frame_processors:
            del self.frame_processors[client_id]
        if client_id in self.last_detection_time:
            del self.last_detection_time[client_id]
        print(f"❌ Client {client_id} disconnected. Total: {len(self.active_connections)}")
    
    async def send_message(self, client_id: str, message: dict):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

manager = ConnectionManager()
music_service = MusicService()

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for receiving video frames"""
    client_id = str(id(websocket))
    
    await manager.connect(websocket, client_id)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "WebSocket connection established"
        })
        
        # Get mood detector from app state (via websocket.app)
        mood_detector = websocket.app.state.mood_detector
        frame_processor = manager.frame_processors[client_id]
        
        while True:
            # Receive frame data (binary blob)
            data = await websocket.receive()
            
            if "bytes" in data:
                frame_data = data["bytes"]
                current_time = time.time()
                
                # Process frame
                try:
                    # Convert bytes to image
                    image = Image.open(io.BytesIO(frame_data))
                    img_array = np.array(image)
                    
                    # Check if we should run detection (throttle based on interval)
                    time_since_last = current_time - manager.last_detection_time.get(client_id, 0)
                    from app.config import settings
                    
                    should_detect = time_since_last >= (settings.DETECTION_INTERVAL / 1000.0)
                    
                    if should_detect:
                        # Run mood detection
                        mood_result = mood_detector.detect_mood(img_array)
                        manager.last_detection_time[client_id] = current_time
                        
                        if mood_result and mood_result.get("success"):
                            mood = mood_result["dominant_emotion"]
                            confidence = float(mood_result["confidence"])  # Convert to Python float
                            
                            # Get song recommendation
                            song = music_service.get_song_for_mood(mood)
                            
                            # Convert all emotions to Python floats
                            all_emotions = {
                                k: float(v) for k, v in mood_result.get("emotions", {}).items()
                            }
                            
                            # Send result back to client
                            await websocket.send_json({
                                "type": "mood_detected",
                                "mood": mood,
                                "confidence": confidence,
                                "song": song,
                                "timestamp": datetime.now().isoformat(),
                                "all_emotions": all_emotions
                            })
                            
                            print(f"🎭 Detected mood: {mood} ({confidence:.2%}) for client {client_id}")
                            print(f"🎵 Recommended: {song}")
                    
                    # Send frame acknowledgment
                    await websocket.send_json({
                        "type": "frame_ack",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    print(f"❌ Error processing frame: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif "text" in data:
                # Handle text messages (ping/pong, control)
                try:
                    msg = json.loads(data["text"])
                    if msg.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    pass
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(client_id)