"use client";

import { CameraSettings, StreamStats } from "@/Types";
import { useEffect, useRef, useState } from "react";
import StatusIndicator from "./StatusIndicator";
import { Camera, Settings, Square, Video, VideoOff } from "lucide-react";
import SettingsPanel from "./SettingsPanel";

const CameraStreamApp = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const [isStreaming, setIsStreaming] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [stats, setStats] = useState<StreamStats>({
    framesSent: 0,
    fps: 0,
    isConnected: false,
    latency: 0,
  });

  const [settings, setSettings] = useState<CameraSettings>({
    fps: 10,
    quality: 0.8,
    resolution: "1280x720",
    backendUrl: "ws://localhost:8000/stream",
  });

  // Start Camera
  const startCamera = async () => {
    try {
      setError(null);
      const [width, height] = settings.resolution.split("x").map(Number);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: width },
          height: { ideal: height },
        },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsCameraOn(true);
      }
    } catch (err) {
      setError("Failed to access camera. Please grant permission.");
      console.error("Camera error:", err);
    }
  };

  // Stop Camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
    stopStreaming();
  };

  // Connect WebSocket
  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(settings.backendUrl);

      ws.onopen = () => {
        setStats((prev) => ({ ...prev, isConnected: true }));
      };

      ws.onclose = () => {
        setStats((prev) => ({ ...prev, isConnected: false }));
      };

      ws.onerror = (err) => {
        setError("WebSocket connection failed");
        console.error("WebSocket error:", err);
      };

      wsRef.current = ws;
    } catch (err) {
      setError("Failed to connect to backend");
      console.error("WebSocket error:", err);
    }
  };

  // Capture and Send Frame
  const captureAndSendFrame = () => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (!ctx || video.readyState !== video.HAVE_ENOUGH_DATA) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(
      (blob) => {
        if (blob && wsRef.current?.readyState === WebSocket.OPEN) {
          const startTime = Date.now();
          wsRef.current.send(blob);

          setStats((prev) => ({
            ...prev,
            framesSent: prev.framesSent + 1,
            latency: Date.now() - startTime,
          }));
        }
      },
      "image/jpeg",
      settings.quality
    );
  };

  // Start Streaming
  const startStreaming = () => {
    if (!isCameraOn) {
      setError("Please start camera first");
      return;
    }

    connectWebSocket();

    const interval = setInterval(() => {
      captureAndSendFrame();
    }, 1000 / settings.fps);

    intervalRef.current = interval;
    setIsStreaming(true);
    setStats((prev) => ({ ...prev, fps: settings.fps, framesSent: 0 }));
  };

  // Stop Streaming
  const stopStreaming = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsStreaming(false);
    setStats((prev) => ({ ...prev, isConnected: false, framesSent: 0 }));
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
      stopStreaming();
    };
  }, []);

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Video Display */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-full max-w-4xl aspect-video bg-black/50 rounded-2xl overflow-hidden shadow-2xl border border-white/10">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          {!isCameraOn && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Camera className="w-16 h-16 text-white/20 mx-auto mb-4" />
                <p className="text-white/40 text-lg">Camera Off</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Hidden Canvas for Frame Capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Status Indicator */}
      {isCameraOn && <StatusIndicator stats={stats} />}

      {/* Frames Counter */}
      {isStreaming && (
        <div className="absolute top-4 right-4 bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
          <span className="text-xs text-white/80 font-medium">
            Frames: {stats.framesSent}
          </span>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-red-500/20 backdrop-blur-md px-6 py-3 rounded-full border border-red-500/30">
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {/* Controls */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-4">
        {/* Camera Toggle */}
        <button
          onClick={isCameraOn ? stopCamera : startCamera}
          className={`p-4 rounded-full backdrop-blur-md border transition-all ${
            isCameraOn
              ? "bg-red-500/20 border-red-500/30 hover:bg-red-500/30"
              : "bg-blue-500/20 border-blue-500/30 hover:bg-blue-500/30"
          }`}
        >
          {isCameraOn ? (
            <VideoOff className="w-6 h-6 text-red-300" />
          ) : (
            <Video className="w-6 h-6 text-blue-300" />
          )}
        </button>

        {/* Stream Toggle */}
        <button
          onClick={isStreaming ? stopStreaming : startStreaming}
          disabled={!isCameraOn}
          className={`px-8 py-4 rounded-full backdrop-blur-md border transition-all font-semibold ${
            !isCameraOn
              ? "bg-gray-500/20 border-gray-500/30 text-gray-400 cursor-not-allowed"
              : isStreaming
              ? "bg-red-500/20 border-red-500/30 text-red-300 hover:bg-red-500/30"
              : "bg-green-500/20 border-green-500/30 text-green-300 hover:bg-green-500/30"
          }`}
        >
          {isStreaming ? (
            <div className="flex items-center gap-2">
              <Square className="w-5 h-5" />
              Stop Stream
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              Start Stream
            </div>
          )}
        </button>

        {/* Settings */}
        <button
          onClick={() => setShowSettings(true)}
          className="p-4 rounded-full bg-gray-500/20 backdrop-blur-md border border-gray-500/30 hover:bg-gray-500/30 transition-all"
        >
          <Settings className="w-6 h-6 text-gray-300" />
        </button>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <SettingsPanel
          settings={settings}
          onSettingsChange={setSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
};

export default CameraStreamApp;
