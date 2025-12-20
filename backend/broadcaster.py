"""
WebSocket Broadcaster
Broadcasts Dita terminal status to connected web clients
"""
import asyncio
import json
from typing import Set
from fastapi import WebSocket


class DitaBroadcaster:
    def __init__(self):
        self.connections: Set[WebSocket] = set()
        self.current_state = "idle"
        self.current_transcript = ""
        self.current_response = ""
        self.loop = None
        
    async def connect(self, websocket: WebSocket):
        """Add new WebSocket connection"""
        await websocket.accept()
        self.connections.add(websocket)
        
        # Send current state to new connection
        await self.send_to_client(websocket, {
            "type": "state",
            "state": self.current_state
        })
        
        if self.current_transcript:
            await self.send_to_client(websocket, {
                "type": "transcription",
                "text": self.current_transcript
            })
        
        if self.current_response:
            await self.send_to_client(websocket, {
                "type": "response",
                "text": self.current_response
            })
        
        print(f"Client connected. Total connections: {len(self.connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connections:
            self.connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.connections)}")
    
    async def send_to_client(self, websocket: WebSocket, data: dict):
        """Send data to specific client"""
        try:
            await websocket.send_json(data)
        except:
            self.disconnect(websocket)
    
    async def broadcast(self, data: dict):
        """Broadcast data to all connected clients"""
        if not self.connections:
            return
        
        disconnected = set()
        for connection in self.connections:
            try:
                await connection.send_json(data)
            except:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    def broadcast_sync(self, data: dict):
        """
        Synchronous broadcast (can be called from terminal thread)
        """
        if not self.loop or not self.connections:
            return
        
        try:
            asyncio.run_coroutine_threadsafe(
                self.broadcast(data),
                self.loop
            )
        except Exception as e:
            print(f"Broadcast error: {e}")

    def set_loop(self, loop):
        """Set the event loop (called from FastAPI startup)"""
        self.loop = loop
    
    # Public API for terminal to call
    def update_state(self, state: str):
        """Update Dita state"""
        self.current_state = state
        self.broadcast_sync({
            "type": "state",
            "state": state
        })
        print(f"Broadcasting state: {state}")
    
    def update_transcript(self, text: str):
        """Update transcription"""
        self.current_transcript = text
        self.broadcast_sync({
            "type": "transcription",
            "text": text
        })
        print(f"Broadcasting transcript: {text[:50]}...")
    
    def update_response(self, text: str):
        """Update response"""
        self.current_response = text
        self.broadcast_sync({
            "type": "response",
            "text": text
        })
        print(f"Broadcasting response: {text[:50]}...")
    
    def clear_content(self):
        """Clear transcript and response"""
        self.current_transcript = ""
        self.current_response = ""
        self.broadcast_sync({
            "type": "clear"
        })
    
    def broadcast_session_event(self, event: str, user_data: dict = None):
        """Broadcast session events (login, logout, switch)"""
        data = {
            "type": "session",
            "event": event,  # 'login', 'logout', 'switch'
            "user": user_data
        }
        self.broadcast_sync(data)
        print(f"Broadcasting session event: {event}")


# Global broadcaster instance
broadcaster = DitaBroadcaster()
