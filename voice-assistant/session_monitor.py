"""
Session Monitor - Listen to WebSocket for real-time session changes
"""
import websocket
import json
import threading
import time
from typing import Callable, Optional


class SessionMonitor:
    """Monitor session changes via WebSocket"""
    
    def __init__(self, backend_url: str):
        """
        Initialize session monitor
        
        Args:
            backend_url: Backend URL (e.g., http://localhost:8000)
        """
        self.backend_url = backend_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.ws_url = f"{self.backend_url}/ws/dashboard"
        self.ws = None
        self.thread = None
        self.running = False
        
        # Callbacks
        self.on_login: Optional[Callable] = None
        self.on_logout: Optional[Callable] = None
        self.on_switch: Optional[Callable] = None
    
    def start(self):
        """Start monitoring session changes"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("✓ Session monitor started")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.ws:
            self.ws.close()
        print("✓ Session monitor stopped")
    
    def _run(self):
        """Main loop for WebSocket connection"""
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )
                self.ws.run_forever()
            except Exception as e:
                print(f"Session monitor error: {e}")
            
            if self.running:
                print("Reconnecting to session monitor in 5s...")
                time.sleep(5)
    
    def _on_open(self, ws):
        """Called when WebSocket connection opens"""
        print("✓ Connected to session monitor")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'session':
                event = data.get('event')
                user_data = data.get('user', {})
                
                if event == 'login' and self.on_login:
                    self.on_login(user_data)
                elif event == 'logout' and self.on_logout:
                    self.on_logout(user_data)
                elif event == 'switch' and self.on_switch:
                    self.on_switch(user_data)
        
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Error handling session event: {e}")
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        if self.running:
            print(f"Session monitor connection error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        if self.running:
            print("Session monitor disconnected")
