"""
Authentication Module for Dita Voice Assistant
Handles user authentication and permission validation with backend API
"""
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class TokenExpiredError(Exception):
    """Raised when token has expired"""
    pass


class DitaAuthClient:
    """Client for handling authentication with Dita backend API"""
    
    def __init__(self, backend_url: str):
        """
        Initialize authentication client
        
        Args:
            backend_url: Base URL of backend API (e.g., http://localhost:8000)
        """
        self.backend_url = backend_url.rstrip('/')
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_context: Optional[Dict[str, Any]] = None
        self.token_expiry: Optional[datetime] = None
    
    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username and password
        
        Args:
            username: User's username
            password: User's password
        
        Returns:
            User context dictionary with role and permissions
        
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                # Set token expiry (15 minutes for access token)
                self.token_expiry = datetime.now() + timedelta(minutes=15)
                
                # Get user profile
                self.user_context = self._get_user_profile()
                
                print(f"✓ Authentication successful: {self.user_context['username']}")
                print(f"  Role: {self.user_context['role']['name']}")
                print(f"  Permissions: {', '.join(self.user_context['role']['permissions'])}")
                
                return self.user_context
            
            elif response.status_code == 401:
                print("✗ Authentication failed: Invalid credentials")
                raise AuthenticationError("Invalid credentials")
            elif response.status_code == 422:
                print("✗ Authentication failed: Invalid request format")
                raise AuthenticationError("Invalid request format")
            else:
                print(f"✗ Authentication failed: HTTP {response.status_code}")
                raise AuthenticationError(f"HTTP {response.status_code}")
        
        except requests.RequestException as e:
            print(f"✗ Cannot connect to backend API: {e}")
            raise AuthenticationError(f"Cannot connect to backend: {e}")
    
    def _get_user_profile(self) -> Dict[str, Any]:
        """
        Get user profile from backend
        
        Returns:
            User profile dictionary
        
        Raises:
            AuthenticationError: If request fails
        """
        try:
            response = requests.get(
                f"{self.backend_url}/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise AuthenticationError(f"Failed to get user profile: {response.status_code}")
        
        except requests.RequestException as e:
            raise AuthenticationError(f"Cannot get user profile: {e}")
    
    def validate_token(self) -> bool:
        """
        Check if access token is still valid
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.access_token:
            return False
        
        # Check expiry time
        if self.token_expiry and datetime.now() >= self.token_expiry:
            print("⚠ Access token expired, attempting to refresh...")
            return self.refresh_access_token()
        
        # Validate token with backend
        try:
            response = requests.get(
                f"{self.backend_url}/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            return response.status_code == 200
        
        except requests.RequestException:
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token
        
        Returns:
            True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{self.backend_url}/auth/refresh",
                json={"refresh_token": self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.token_expiry = datetime.now() + timedelta(minutes=15)
                print("✓ Access token refreshed successfully")
                return True
            else:
                print(f"✗ Token refresh failed: {response.status_code}")
                return False
        
        except requests.RequestException as e:
            print(f"✗ Token refresh error: {e}")
            return False
    
    def get_user_context(self) -> Optional[Dict[str, Any]]:
        """
        Get current user context
        
        Returns:
            User context dictionary or None if not authenticated
        """
        return self.user_context
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            permission: Permission name to check (e.g., "send_whatsapp")
        
        Returns:
            True if user has permission, False otherwise
        """
        if not self.user_context:
            return False
        
        permissions = self.user_context.get("role", {}).get("permissions", {})
        # Permissions is a dict like {"send_whatsapp": True, "broadcast_all": False}
        # Check if permission exists and is True
        return permissions.get(permission, False) == True
    
    def can_send_to_contact(self, contact_id: int) -> bool:
        """
        Check if user can send message to specific WhatsApp contact
        
        Args:
            contact_id: WhatsApp contact ID
        
        Returns:
            True if user can send to contact, False otherwise
        """
        if not self.access_token:
            return False
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/contacts",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                contacts = response.json()
                # Check if contact exists and user has access
                for contact in contacts:
                    if contact["id"] == contact_id and contact.get("is_active", False):
                        return True
                return False
            else:
                return False
        
        except requests.RequestException:
            return False
    
    def get_available_contacts(self) -> list:
        """
        Get list of WhatsApp contacts available to user
        
        Returns:
            List of contact dictionaries
        """
        if not self.access_token:
            return []
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/contacts",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        
        except requests.RequestException:
            return []
    
    def log_action(self, action: str, resource: str, details: Dict[str, Any]) -> bool:
        """
        Log user action to audit log
        
        Args:
            action: Action performed (e.g., "send_whatsapp", "search_news")
            resource: Resource accessed (e.g., "whatsapp", "news")
            details: Additional details as dictionary
        
        Returns:
            True if logging successful, False otherwise
        """
        if not self.access_token:
            return False
        
        try:
            # Note: Backend needs endpoint for creating audit logs from voice assistant
            # For now, this is a placeholder
            print(f"[AUDIT] User: {self.user_context['username']} | Action: {action} | Resource: {resource}")
            print(f"[AUDIT] Details: {json.dumps(details, indent=2)}")
            return True
        
        except Exception as e:
            print(f"✗ Audit log error: {e}")
            return False
    
    def logout(self) -> bool:
        """
        Logout user and clear tokens
        
        Returns:
            True if logout successful, False otherwise
        """
        if not self.access_token:
            return False
        
        try:
            response = requests.post(
                f"{self.backend_url}/auth/logout",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            
            # Clear local tokens regardless of response
            self.access_token = None
            self.refresh_token = None
            self.user_context = None
            self.token_expiry = None
            
            if response.status_code == 200:
                print("✓ Logout successful")
                return True
            else:
                print(f"⚠ Logout completed locally (backend response: {response.status_code})")
                return True
        
        except requests.RequestException as e:
            # Clear tokens even if request fails
            self.access_token = None
            self.refresh_token = None
            self.user_context = None
            self.token_expiry = None
            print(f"⚠ Logout completed locally (error: {e})")
            return True
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated
        
        Returns:
            True if authenticated with valid token, False otherwise
        """
        return self.access_token is not None and self.validate_token()


def authenticate_terminal_user(backend_url: str) -> Optional[DitaAuthClient]:
    """
    Interactive terminal authentication for Dita voice assistant
    
    Args:
        backend_url: Base URL of backend API
    
    Returns:
        Authenticated DitaAuthClient instance or None if authentication failed
    """
    print("\n" + "="*60)
    print("DITA VOICE ASSISTANT - AUTHENTICATION")
    print("="*60)
    print(f"Backend API: {backend_url}")
    print()
    
    auth_client = DitaAuthClient(backend_url)
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            username = input(f"Username [{attempt}/{max_attempts}]: ").strip()
            password = input(f"Password [{attempt}/{max_attempts}]: ").strip()
            
            if not username or not password:
                print("✗ Username and password are required")
                continue
            
            print("\nAuthenticating...")
            auth_client.authenticate(username, password)
            
            print("\n" + "="*60)
            print("AUTHENTICATION SUCCESSFUL")
            print("="*60)
            return auth_client
        
        except AuthenticationError as e:
            print(f"\n✗ Authentication failed: {e}")
            if attempt < max_attempts:
                print(f"Please try again ({max_attempts - attempt} attempts remaining)\n")
            else:
                print(f"\n✗ Maximum authentication attempts reached")
                return None
        
        except KeyboardInterrupt:
            print("\n\n✗ Authentication cancelled by user")
            return None
        
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            return None
    
    return None
