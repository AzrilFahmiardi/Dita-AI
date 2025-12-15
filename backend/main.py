"""
Dita AI Assistant - FastAPI Backend (Display-only mode)
WebSocket-based status broadcaster for web dashboard
Terminal assistant handles all audio processing
"""
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from broadcaster import broadcaster

# Configuration
DASHBOARD_HOST = '0.0.0.0'
DASHBOARD_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000"
]

app = FastAPI(
    title="Dita AI Assistant Dashboard API",
    description="Real-time status dashboard for Dita terminal assistant",
    version="2.0.0"
)

# CORS configuration from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Set event loop for broadcaster"""
    broadcaster.set_loop(asyncio.get_event_loop())
    print("Dita Dashboard Backend ready!")
    print("Terminal assistant will broadcast status to this server")
    print(f"Dashboard available at http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    print(f"CORS origins: {CORS_ORIGINS}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Dita AI Assistant Dashboard",
        "version": "2.0.0",
        "mode": "display-only",
        "connections": len(broadcaster.connections),
        "current_state": broadcaster.current_state
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "connections": len(broadcaster.connections),
        "current_state": broadcaster.current_state
    }


@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for dashboard (display-only)
    Frontend subscribes to receive status updates from terminal
    """
    await broadcaster.connect(websocket)
    
    try:
        while True:
            # Just keep connection alive
            # All updates are pushed from terminal via broadcaster
            data = await websocket.receive_text()
            
            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
        print("Dashboard client disconnected")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        broadcaster.disconnect(websocket)


@app.get("/api/status")
async def get_status():
    """Get current Dita status"""
    return {
        "state": broadcaster.current_state,
        "transcript": broadcaster.current_transcript,
        "response": broadcaster.current_response,
        "connections": len(broadcaster.connections)
    }


@app.post("/api/broadcast/state")
async def broadcast_state(data: dict):
    """Receive state update from terminal and broadcast to clients"""
    state = data.get("state")
    if state:
        broadcaster.update_state(state)
        return {"status": "ok", "connections": len(broadcaster.connections)}
    return {"status": "error", "message": "No state provided"}


@app.post("/api/broadcast/transcript")
async def broadcast_transcript(data: dict):
    """Receive transcript from terminal and broadcast to clients"""
    text = data.get("text")
    if text:
        broadcaster.update_transcript(text)
        return {"status": "ok", "connections": len(broadcaster.connections)}
    return {"status": "error", "message": "No text provided"}


@app.post("/api/broadcast/response")
async def broadcast_response(data: dict):
    """Receive response from terminal and broadcast to clients"""
    text = data.get("text")
    if text:
        broadcaster.update_response(text)
        return {"status": "ok", "connections": len(broadcaster.connections)}
    return {"status": "error", "message": "No text provided"}


@app.post("/api/broadcast/clear")
async def broadcast_clear():
    """Clear transcript and response"""
    broadcaster.clear_content()
    return {"status": "ok", "connections": len(broadcaster.connections)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=DASHBOARD_HOST, port=DASHBOARD_PORT)
