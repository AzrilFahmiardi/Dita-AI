/**
 * Configuration loaded from environment variables
 * Uses Vite's import.meta.env to access .env variables
 */

export const config = {
  websocket: {
    url: import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws/dashboard',
    reconnectInterval: parseInt(import.meta.env.VITE_RECONNECT_INTERVAL || '3000'),
    pingInterval: parseInt(import.meta.env.VITE_PING_INTERVAL || '30000'),
  },
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  },
};

// Log configuration on load (for debugging)
if (import.meta.env.DEV) {
  console.log('🔧 Dashboard Configuration:', config);
}
