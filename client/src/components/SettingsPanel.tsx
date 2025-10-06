"use client";

import { CameraSettings } from "@/Types";
import { useState } from "react";

const SettingsPanel = ({
  settings,
  onSettingsChange,
  onClose,
}: {
  settings: CameraSettings;
  onSettingsChange: (settings: CameraSettings) => void;
  onClose: () => void;
}) => {
  const [localSettings, setLocalSettings] = useState(settings);

  const handleSave = () => {
    onSettingsChange(localSettings);
    onClose();
  };

  return (
    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 w-full max-w-md border border-white/10 shadow-2xl">
        <h2 className="text-2xl font-bold text-white mb-6">Settings</h2>

        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-300 mb-2 block">
              Frame Rate (FPS)
            </label>
            <input
              type="range"
              min="1"
              max="30"
              value={localSettings.fps}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  fps: Number(e.target.value),
                })
              }
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <span className="text-white text-sm">{localSettings.fps} fps</span>
          </div>

          <div>
            <label className="text-sm text-gray-300 mb-2 block">Quality</label>
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.1"
              value={localSettings.quality}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  quality: Number(e.target.value),
                })
              }
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <span className="text-white text-sm">
              {Math.round(localSettings.quality * 100)}%
            </span>
          </div>

          <div>
            <label className="text-sm text-gray-300 mb-2 block">
              Resolution
            </label>
            <select
              value={localSettings.resolution}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  resolution: e.target.value,
                })
              }
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="640x480">640x480</option>
              <option value="1280x720">1280x720 (HD)</option>
              <option value="1920x1080">1920x1080 (Full HD)</option>
            </select>
          </div>

          <div>
            <label className="text-sm text-gray-300 mb-2 block">
              Backend URL
            </label>
            <input
              type="text"
              value={localSettings.backendUrl}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  backendUrl: e.target.value,
                })
              }
              placeholder="ws://localhost:8000/stream"
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-700 hover:bg-gray-600 text-white rounded-lg py-2 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-2 transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
