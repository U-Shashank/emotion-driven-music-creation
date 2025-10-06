import { Wifi, WifiOff } from "lucide-react";
import { StreamStats } from "@/Types";

const StatusIndicator = ({ stats }: { stats: StreamStats }) => {
  return (
    <div className="absolute top-4 left-4 flex items-center gap-3 bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
      {stats.isConnected ? (
        <>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <Wifi className="w-4 h-4 text-green-400" />
          </div>
          <div className="h-4 w-px bg-white/20" />
          <span className="text-xs text-white/80 font-medium">
            {stats.fps} FPS
          </span>
          <div className="h-4 w-px bg-white/20" />
          <span className="text-xs text-white/80 font-medium">
            {stats.latency}ms
          </span>
        </>
      ) : (
        <>
          <WifiOff className="w-4 h-4 text-red-400" />
          <span className="text-xs text-red-400 font-medium">Disconnected</span>
        </>
      )}
    </div>
  );
};

export default StatusIndicator;
