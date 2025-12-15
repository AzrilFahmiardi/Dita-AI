"""
Fonnte WhatsApp API Client
Handles sending messages via Fonnte service
"""

import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class FontteClient:
    """Client for Fonnte WhatsApp API"""
    
    def __init__(self):
        self.api_token = os.getenv('FONNTE_API_TOKEN')
        self.api_url = "https://api.fonnte.com/send"
        self.timeout = 30
        
        if not self.api_token:
            raise ValueError("FONNTE_API_TOKEN not found in environment variables")
    
    def send_message(
        self, 
        phone_number: str, 
        message: str,
        validate_number: bool = True
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message via Fonnte
        
        Args:
            phone_number: Target phone number (format: 628xxx or 08xxx)
            message: Message text to send
            validate_number: Whether to validate phone number format
            
        Returns:
            Dict with status and response data
        """
        try:
            # Normalize phone number
            normalized_number = self._normalize_phone_number(phone_number)
            
            if validate_number and not self._is_valid_phone_number(normalized_number):
                return {
                    "status": "error",
                    "message": f"Invalid phone number format: {phone_number}"
                }
            
            # Prepare request
            headers = {
                "Authorization": self.api_token
            }
            
            payload = {
                "target": normalized_number,
                "message": message,
                "countryCode": "62"
            }
            
            # Send request
            response = requests.post(
                self.api_url,
                headers=headers,
                data=payload,
                timeout=self.timeout
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "message": "Message sent successfully",
                    "phone_number": normalized_number,
                    "response": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.Timeout:
            return {
                "status": "error",
                "message": "Request timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send message: {str(e)}"
            }
    
    def _normalize_phone_number(self, phone_number: str) -> str:
        """
        Normalize phone number to 62xxx format
        
        Args:
            phone_number: Input phone number
            
        Returns:
            Normalized phone number
        """
        # Remove spaces, dashes, and other characters
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Convert 08xxx to 628xxx
        if cleaned.startswith('08'):
            cleaned = '62' + cleaned[1:]
        
        # Add 62 prefix if missing
        if not cleaned.startswith('62'):
            cleaned = '62' + cleaned
        
        return cleaned
    
    def _is_valid_phone_number(self, phone_number: str) -> bool:
        """
        Validate Indonesian phone number format
        
        Args:
            phone_number: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Should start with 62 and have 10-13 digits total
        if not phone_number.startswith('62'):
            return False
        
        if len(phone_number) < 11 or len(phone_number) > 15:
            return False
        
        return True
