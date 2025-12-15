"""
Dita AI Assistant - FastAPI Backend (Display-only mode)
WebSocket-based status broadcaster for web dashboard
Terminal assistant handles all audio processing
"""
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from broadcaster import broadcaster
from database import get_db
from database.models import User, AuditLog
from auth.security import verify_password, create_access_token, create_refresh_token, verify_token
from auth.dependencies import get_current_active_user
from auth.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserProfileResponse,
    RoleSchema,
    WhatsAppContactSchema,
    UserContactSchema
)

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


# Authentication Endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        login_data: Username and password
        db: Database session
        
    Returns:
        Access token and refresh token
    """
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        resource="auth",
        details={"username": user.username}
    )
    db.add(audit_log)
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=15 * 60
    )


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token
        db: Database session
        
    Returns:
        New access token and refresh token
    """
    payload = verify_token(refresh_data.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=15 * 60
    )


@app.get("/auth/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile with role and allowed contacts.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Complete user profile with permissions and contacts
    """
    user_contacts = []
    for uc in current_user.user_contacts:
        user_contacts.append(UserContactSchema(
            contact=WhatsAppContactSchema(
                id=uc.contact.id,
                name=uc.contact.name,
                phone_number=uc.contact.phone_number,
                is_active=uc.contact.is_active
            ),
            can_send=uc.can_send
        ))
    
    return UserProfileResponse(
        id=current_user.id,
        nrp=current_user.nrp,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role=RoleSchema(
            id=current_user.role.id,
            name=current_user.role.name,
            level=current_user.role.level,
            permissions=current_user.role.permissions
        ),
        contacts=user_contacts,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@app.post("/auth/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user (client should discard tokens).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    audit_log = AuditLog(
        user_id=current_user.id,
        action="logout",
        resource="auth",
        details={"username": current_user.username}
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Successfully logged out"}


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
