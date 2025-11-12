import { useState, useEffect, useCallback } from 'react';
import { WebSocketService } from '../services/websocket';

export function useVoiceAgent() {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [wsService, setWsService] = useState<WebSocketService | null>(null);

  useEffect(() => {
    const service = new WebSocketService();
    setWsService(service);

    const messageHandler = (data: any) => {
      if (data.type === 'response') {
        setMessages((prev) => [...prev, { role: 'assistant', content: data.message }]);
      } else if (data.type === 'connection') {
        setIsConnected(true);
      } else if (data.type === 'error') {
        setMessages((prev) => [...prev, { role: 'assistant', content: data.message }]);
      }
    };

    service.connect()
      .then(() => {
        setIsConnected(true);
        service.onMessage(messageHandler);
      })
      .catch((error) => {
        console.error('Failed to connect:', error);
        setIsConnected(false);
      });

    return () => {
      service.offMessage(messageHandler);
      service.disconnect();
    };
  }, []);

  const sendMessage = useCallback((message: string) => {
    if (wsService && isConnected) {
      setMessages((prev) => [...prev, { role: 'user', content: message }]);
      wsService.sendMessage(message);
    }
  }, [wsService, isConnected]);

  return {
    isConnected,
    messages,
    sendMessage,
  };
}

