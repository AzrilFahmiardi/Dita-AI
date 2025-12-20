import { useState, useEffect, useRef, useCallback } from 'react';
import { config } from '../config';

// Load configuration from config helper
const WS_URL = config.websocket.url;
const RECONNECT_INTERVAL = config.websocket.reconnectInterval;
const PING_INTERVAL = config.websocket.pingInterval;

export const useVoiceChat = () => {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [ditaState, setDitaState] = useState('idle');
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        console.log('Connected to Dita Dashboard at', WS_URL);
        setConnectionStatus('connected');
        
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, PING_INTERVAL);
        
        ws.pingInterval = pingInterval;
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          console.log('Received:', data);
          
          switch (data.type) {
            case 'state':
              setDitaState(data.state);
              break;
            
            case 'transcription':
              setTranscript(data.text);
              break;
            
            case 'response':
              setResponse(data.text);
              break;
            
            case 'clear':
              setTranscript('');
              setResponse('');
              break;
            
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };
      
      ws.onclose = () => {
        console.log('Disconnected from Dita Dashboard');
        setConnectionStatus('disconnected');
        
        if (ws.pingInterval) {
          clearInterval(ws.pingInterval);
        }
        
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, RECONNECT_INTERVAL);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionStatus('error');
      
      // Retry connection at configured interval
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, RECONNECT_INTERVAL);
    }
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (wsRef.current) {
        if (wsRef.current.pingInterval) {
          clearInterval(wsRef.current.pingInterval);
        }
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    connectionStatus,
    ditaState,
    transcript,
    response,
  };
};
