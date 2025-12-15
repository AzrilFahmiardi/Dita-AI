"""
Broadcast Client for Terminal
Sends updates to dashboard backend via HTTP
"""
import requests
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import get_config

# Load dashboard config
config = get_config()
dashboard_config = config.get('dashboard', {})
backend_config = dashboard_config.get('backend', {})
frontend_config = dashboard_config.get('frontend', {})

DASHBOARD_HOST = backend_config.get('host', '0.0.0.0')
DASHBOARD_PORT = backend_config.get('port', 8000)
DASHBOARD_URL = frontend_config.get('api_base_url', f"http://localhost:{DASHBOARD_PORT}")


class BroadcastClient:
    """Client to send updates to dashboard backend"""
    
    def __init__(self, dashboard_url: str = DASHBOARD_URL):
        self.dashboard_url = dashboard_url
        self.enabled = True
        
        # Test connection
        try:
            response = requests.get(f"{dashboard_url}/health", timeout=1)
            if response.status_code == 200:
                print(f"Connected to dashboard at {dashboard_url}")
            else:
                print(f"Dashboard responded with status {response.status_code}")
                self.enabled = False
        except Exception as e:
            print(f"Dashboard not available: {e}")
            print("   Terminal will work without dashboard")
            self.enabled = False
    
    def update_state(self, state: str):
        """Update Dita state"""
        if not self.enabled:
            return
        
        try:
            requests.post(
                f"{self.dashboard_url}/api/broadcast/state",
                json={"state": state},
                timeout=1
            )
            print(f"Broadcasting state: {state}")
        except Exception as e:
            print(f"Failed to broadcast state: {e}")
    
    def update_transcript(self, text: str):
        """Update user transcript"""
        if not self.enabled:
            return
        
        try:
            # Truncate for display
            display_text = text[:100] + "..." if len(text) > 100 else text
            requests.post(
                f"{self.dashboard_url}/api/broadcast/transcript",
                json={"text": text},
                timeout=1
            )
            print(f"Broadcasting transcript: {display_text}")
        except Exception as e:
            print(f"Failed to broadcast transcript: {e}")

    def update_response(self, text: str):
        """Update Dita response"""
        if not self.enabled:
            return
        
        try:
            # Truncate for display
            display_text = text[:100] + "..." if len(text) > 100 else text
            requests.post(
                f"{self.dashboard_url}/api/broadcast/response",
                json={"text": text},
                timeout=1
            )
            print(f"Broadcasting response: {display_text}")
        except Exception as e:
            print(f"Failed to broadcast response: {e}")

    def clear_content(self):
        """Clear transcript and response"""
        if not self.enabled:
            return
        
        try:
            requests.post(
                f"{self.dashboard_url}/api/broadcast/clear",
                timeout=1
            )
        except Exception as e:
            print(f"Failed to clear content: {e}")


# Global instance
broadcast_client = BroadcastClient()
