/**
 * Real-time Data Stream Manager
 * WebSocket integration for live updates across visualization components
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface StreamMessage {
  type: 'entity_update' | 'transaction' | 'risk_alert' | 'compliance_event';
  timestamp: string;
  data: any;
  source: string;
}

export interface StreamSubscription {
  id: string;
  channel: string;
  callback: (message: StreamMessage) => void;
  filters?: Record<string, any>;
}

class DataStreamManager {
  public ws: WebSocket | null = null;
  private subscriptions: Map<string, StreamSubscription> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000;
  private isConnecting = false;

  constructor(private baseUrl: string = 'ws://localhost:4000') {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
        resolve();
        return;
      }

      this.isConnecting = true;

      try {
        this.ws = new WebSocket(`${this.baseUrl}/ws/stream`);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected to data stream');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          // Resubscribe to all channels
          this.subscriptions.forEach(sub => {
            this.sendSubscription(sub);
          });

          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: StreamMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse stream message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('🔌 WebSocket disconnected from data stream');
          this.isConnecting = false;
          this.ws = null;
          this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, this.reconnectInterval);
  }

  private sendSubscription(subscription: StreamSubscription): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }

    const message = {
      type: 'subscribe',
      channel: subscription.channel,
      filters: subscription.filters || {}
    };

    this.ws.send(JSON.stringify(message));
  }

  private handleMessage(message: StreamMessage): void {
    // Route message to all relevant subscriptions
    this.subscriptions.forEach((subscription) => {
      if (this.messageMatchesSubscription(message, subscription)) {
        subscription.callback(message);
      }
    });
  }

  private messageMatchesSubscription(message: StreamMessage, subscription: StreamSubscription): boolean {
    // Simple channel matching for now
    // Could be enhanced with more sophisticated filtering
    return message.type === subscription.channel || 
           subscription.channel === 'all' ||
           message.source === subscription.channel;
  }

  subscribe(subscription: StreamSubscription): () => void {
    this.subscriptions.set(subscription.id, subscription);
    
    // Send subscription if connected
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.sendSubscription(subscription);
    }

    // Return unsubscribe function
    return () => {
      this.subscriptions.delete(subscription.id);
      
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        const message = {
          type: 'unsubscribe',
          channel: subscription.channel
        };
        this.ws.send(JSON.stringify(message));
      }
    };
  }

  disconnect(): void {
    this.subscriptions.clear();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Singleton instance
const streamManager = new DataStreamManager();

// React Hook for using data streams
export function useDataStream(
  channel: string,
  filters?: Record<string, any>
): {
  isConnected: boolean;
  messages: StreamMessage[];
  latestMessage: StreamMessage | null;
  sendMessage: (message: any) => void;
} {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [latestMessage, setLatestMessage] = useState<StreamMessage | null>(null);
  const subscriptionId = useRef(`${channel}-${Date.now()}-${Math.random()}`);

  const handleMessage = useCallback((message: StreamMessage) => {
    setMessages(prev => [...prev.slice(-99), message]); // Keep last 100 messages
    setLatestMessage(message);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (streamManager.ws && streamManager.ws.readyState === WebSocket.OPEN) {
      streamManager.ws.send(JSON.stringify(message));
    }
  }, []);

  useEffect(() => {
    // Connect and subscribe
    streamManager.connect()
      .then(() => {
        setIsConnected(true);
        
        const unsubscribe = streamManager.subscribe({
          id: subscriptionId.current,
          channel,
          callback: handleMessage,
          filters
        });

        return unsubscribe;
      })
      .catch(error => {
        console.error('Failed to connect to data stream:', error);
        setIsConnected(false);
      });

    // Cleanup on unmount
    return () => {
      setIsConnected(false);
    };
  }, [channel, filters, handleMessage]);

  return {
    isConnected,
    messages,
    latestMessage,
    sendMessage
  };
}

// Hook for real-time entity updates
export function useEntityStream(entityId?: string) {
  return useDataStream('entity_update', entityId ? { entity_id: entityId } : undefined);
}

// Hook for transaction stream
export function useTransactionStream(filters?: { address?: string; minValue?: number }) {
  return useDataStream('transaction', filters);
}

// Hook for risk alerts
export function useRiskAlerts(riskThreshold: number = 0.7) {
  return useDataStream('risk_alert', { threshold: riskThreshold });
}

// Hook for compliance events
export function useComplianceStream() {
  return useDataStream('compliance_event');
}

export default streamManager;
