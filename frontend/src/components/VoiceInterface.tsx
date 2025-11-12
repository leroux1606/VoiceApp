import React, { useState } from 'react';
import { Mic, MicOff, Phone, PhoneOff } from 'lucide-react';
import { useLiveKit } from '../hooks/useLiveKit';
import { api } from '../services/api';

interface VoiceInterfaceProps {
  onTranscript?: (text: string) => void;
}

export function VoiceInterface({ onTranscript }: VoiceInterfaceProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isCallActive, setIsCallActive] = useState(false);
  const { room, isConnected, connect, disconnect } = useLiveKit();

  const handleStartCall = async () => {
    try {
      // In a real implementation, you would get the token from your backend
      const response = await api.get('/voice/token');
      await connect('wss://your-livekit-server', response.data.token);
      setIsCallActive(true);
    } catch (error) {
      console.error('Failed to start call:', error);
    }
  };

  const handleEndCall = () => {
    disconnect();
    setIsCallActive(false);
    setIsRecording(false);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Implement actual recording logic here
  };

  return (
    <div className="voice-interface p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-center space-x-4">
        {!isCallActive ? (
          <button
            onClick={handleStartCall}
            className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
          >
            <Phone size={20} />
            <span>Start Call</span>
          </button>
        ) : (
          <>
            <button
              onClick={toggleRecording}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition ${
                isRecording
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
              <span>{isRecording ? 'Stop Recording' : 'Start Recording'}</span>
            </button>
            <button
              onClick={handleEndCall}
              className="flex items-center space-x-2 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              <PhoneOff size={20} />
              <span>End Call</span>
            </button>
          </>
        )}
      </div>

      {isCallActive && (
        <div className="mt-4 text-center">
          <div className={`inline-block w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="ml-2 text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      )}
    </div>
  );
}

