export interface StreamStats {
  framesSent: number;
  fps: number;
  isConnected: boolean;
  latency: number;
}

export interface CameraSettings {
  fps: number;
  quality: number;
  resolution: string;
  backendUrl: string;
}
