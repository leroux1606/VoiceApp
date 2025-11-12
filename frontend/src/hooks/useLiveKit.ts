import { useState, useEffect } from 'react';
import { Room, RoomEvent, RemoteParticipant, LocalParticipant } from 'livekit-client';

export function useLiveKit() {
  const [room, setRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [participants, setParticipants] = useState<RemoteParticipant[]>([]);

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  const connect = async (url: string, token: string) => {
    const newRoom = new Room();
    
    newRoom.on(RoomEvent.Connected, () => {
      setIsConnected(true);
      setParticipants(Array.from(newRoom.remoteParticipants.values()));
    });

    newRoom.on(RoomEvent.Disconnected, () => {
      setIsConnected(false);
      setParticipants([]);
    });

    newRoom.on(RoomEvent.ParticipantConnected, () => {
      setParticipants(Array.from(newRoom.remoteParticipants.values()));
    });

    newRoom.on(RoomEvent.ParticipantDisconnected, () => {
      setParticipants(Array.from(newRoom.remoteParticipants.values()));
    });

    await newRoom.connect(url, token);
    setRoom(newRoom);
  };

  const disconnect = () => {
    if (room) {
      room.disconnect();
      setRoom(null);
      setIsConnected(false);
    }
  };

  return {
    room,
    isConnected,
    participants,
    connect,
    disconnect,
  };
}

