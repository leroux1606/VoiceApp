const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export class WebSocketService {
  private socket: WebSocket | null = null;
  private clientId: string;
  private messageCallbacks: Array<(data: any) => void> = [];

  constructor(clientId: string = `client_${Date.now()}`) {
    this.clientId = clientId;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${WS_URL}/api/ws/${this.clientId}`;
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        resolve();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket connection error:', error);
        reject(error);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.messageCallbacks.forEach((callback) => callback(data));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
      };
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.messageCallbacks = [];
  }

  sendMessage(message: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          type: 'message',
          message,
        })
      );
    }
  }

  onMessage(callback: (data: any) => void): void {
    this.messageCallbacks.push(callback);
  }

  offMessage(callback: (data: any) => void): void {
    this.messageCallbacks = this.messageCallbacks.filter((cb) => cb !== callback);
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

