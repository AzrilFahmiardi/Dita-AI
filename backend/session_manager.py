"""
Session Manager for sharing authentication state between frontend and voice assistant
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


class SessionManager:
    """Manage shared session state between frontend and voice assistant"""
    
    SESSION_FILE = Path.home() / '.dita' / 'session.json'
    
    @classmethod
    def _ensure_dir(cls):
        """Ensure session directory exists"""
        cls.SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def save_session(cls, user_id: int, username: str, token: str, role: str, full_name: str):
        """
        Save active session to shared file
        
        Args:
            user_id: User ID
            username: Username
            token: Access token
            role: User role name
            full_name: User full name
        """
        cls._ensure_dir()
        
        session_data = {
            'user_id': user_id,
            'username': username,
            'token': token,
            'role': role,
            'full_name': full_name,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'frontend'  # Can be 'frontend' or 'voice_assistant'
        }
        
        with open(cls.SESSION_FILE, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    @classmethod
    def get_session(cls) -> Optional[Dict]:
        """
        Get active session from shared file
        
        Returns:
            Session data dict or None if no active session
        """
        if not cls.SESSION_FILE.exists():
            return None
        
        try:
            with open(cls.SESSION_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    @classmethod
    def clear_session(cls):
        """Clear active session"""
        if cls.SESSION_FILE.exists():
            cls.SESSION_FILE.unlink()
    
    @classmethod
    def is_session_valid(cls) -> bool:
        """Check if there's a valid session"""
        session = cls.get_session()
        if not session:
            return False
        
        # Check if session is recent (less than 24 hours old)
        try:
            timestamp = datetime.fromisoformat(session.get('timestamp', ''))
            age = (datetime.utcnow() - timestamp).total_seconds()
            return age < 86400  # 24 hours
        except (ValueError, TypeError):
            return False
