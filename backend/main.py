"""
Dita AI Assistant - FastAPI Backend (Display-only mode)
WebSocket-based status broadcaster for web dashboard
Terminal assistant handles all audio processing
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from broadcaster import broadcaster
from database import get_db
from database.models import User, AuditLog, WhatsAppContact
from auth.security import verify_password, create_access_token, create_refresh_token, verify_token
from auth.dependencies import get_current_active_user, require_permission, require_role_level
from auth.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserProfileResponse,
    RoleSchema,
    WhatsAppContactSchema,
    UserContactSchema,
    UserCreateRequest,
    UserUpdateRequest,
    ChangePasswordRequest,
    ContactCreateRequest,
    ContactUpdateRequest,
    AssignContactRequest,
    UserListResponse,
    AuditLogResponse,
    MessageCreateRequest,
    MessageResponse
)
from services.user_service import UserService
from services.whatsapp_service import WhatsAppService
from services.audit_service import AuditService

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


# User Management Endpoints
@app.get("/api/users", response_model=List[UserListResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of users (requires authentication)"""
    users = UserService.get_users(db, skip, limit, role_id, is_active)
    return [
        UserListResponse(
            id=user.id,
            nrp=user.nrp,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            role=RoleSchema(
                id=user.role.id,
                name=user.role.name,
                level=user.role.level,
                permissions=user.role.permissions
            ),
            last_login=user.last_login
        )
        for user in users
    ]


@app.get("/api/users/search")
async def search_users(
    q: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search users by username, NRP, or full name"""
    users = UserService.search_users(db, q)
    return [
        UserListResponse(
            id=user.id,
            nrp=user.nrp,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            role=RoleSchema(
                id=user.role.id,
                name=user.role.name,
                level=user.role.level,
                permissions=user.role.permissions
            ),
            last_login=user.last_login
        )
        for user in users
    ]


@app.get("/api/users/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_contacts = []
    for uc in user.user_contacts:
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
        id=user.id,
        nrp=user.nrp,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        role=RoleSchema(
            id=user.role.id,
            name=user.role.name,
            level=user.role.level,
            permissions=user.role.permissions
        ),
        contacts=user_contacts,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@app.post("/api/users", response_model=UserListResponse, dependencies=[Depends(require_role_level(1))])
async def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new user (KAPOLRI only)"""
    if UserService.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if UserService.get_user_by_nrp(db, user_data.nrp):
        raise HTTPException(status_code=400, detail="NRP already exists")
    
    user = UserService.create_user(
        db,
        nrp=user_data.nrp,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        role_id=user_data.role_id,
        is_active=user_data.is_active
    )
    
    AuditService.log_action(
        db,
        user_id=current_user.id,
        action="create",
        resource="user",
        details={"created_user_id": user.id, "username": user.username}
    )
    
    return UserListResponse(
        id=user.id,
        nrp=user.nrp,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        role=RoleSchema(
            id=user.role.id,
            name=user.role.name,
            level=user.role.level,
            permissions=user.role.permissions
        ),
        last_login=user.last_login
    )


@app.put("/api/users/{user_id}", dependencies=[Depends(require_role_level(1))])
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user (KAPOLRI only)"""
    user = UserService.update_user(
        db, user_id,
        full_name=user_data.full_name,
        role_id=user_data.role_id,
        is_active=user_data.is_active
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    AuditService.log_action(
        db,
        user_id=current_user.id,
        action="update",
        resource="user",
        details={"updated_user_id": user_id}
    )
    
    return {"message": "User updated successfully"}


@app.post("/api/users/{user_id}/change-password")
async def change_password(
    user_id: int,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password (own or KAPOLRI)"""
    if current_user.id != user_id and current_user.role.level > 1:
        raise HTTPException(status_code=403, detail="Cannot change other user's password")
    
    success = UserService.change_password(db, user_id, password_data.new_password)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    AuditService.log_action(
        db,
        user_id=current_user.id,
        action="change_password",
        resource="user",
        details={"target_user_id": user_id}
    )
    
    return {"message": "Password changed successfully"}


# WhatsApp Contact Endpoints
@app.get("/api/contacts", response_model=List[WhatsAppContactSchema])
async def list_contacts(
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all WhatsApp contacts"""
    contacts = WhatsAppService.get_all_contacts(db, is_active, skip, limit)
    return contacts


@app.post("/api/contacts", response_model=WhatsAppContactSchema, dependencies=[Depends(require_role_level(2))])
async def create_contact(
    contact_data: ContactCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new WhatsApp contact (KAPOLRI/KAPOLDA)"""
    if WhatsAppService.get_contact_by_phone(db, contact_data.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already exists")
    
    contact = WhatsAppService.create_contact(
        db,
        name=contact_data.name,
        phone_number=contact_data.phone_number,
        is_active=contact_data.is_active
    )
    
    AuditService.log_action(
        db,
        user_id=current_user.id,
        action="create",
        resource="contact",
        details={"contact_id": contact.id, "phone": contact.phone_number}
    )
    
    return contact


@app.put("/api/contacts/{contact_id}", dependencies=[Depends(require_role_level(2))])
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update WhatsApp contact (KAPOLRI/KAPOLDA)"""
    contact = WhatsAppService.update_contact(
        db, contact_id,
        name=contact_data.name,
        phone_number=contact_data.phone_number,
        is_active=contact_data.is_active
    )
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    AuditService.log_action(
        db,
        user_id=current_user.id,
        action="update",
        resource="contact",
        details={"contact_id": contact_id}
    )
    
    return {"message": "Contact updated successfully"}


@app.post("/api/contacts/assign", dependencies=[Depends(require_role_level(1))])
async def assign_contact(
    assignment: AssignContactRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Assign contact to user (KAPOLRI only)"""
    user_contact = WhatsAppService.assign_contact_to_user(
        db,
        user_id=assignment.user_id,
        contact_id=assignment.contact_id,
        can_send=assignment.can_send
    )
    
    if not user_contact:
        raise HTTPException(status_code=404, detail="User or contact not found")
    
    AuditService.log_action(
        db,
        user_id=current_user.id,
        action="assign_contact",
        resource="user_contact",
        details={
            "user_id": assignment.user_id,
            "contact_id": assignment.contact_id,
            "can_send": assignment.can_send
        }
    )
    
    return {"message": "Contact assigned successfully"}


# Audit Log Endpoints
@app.get("/api/audit-logs", response_model=List[AuditLogResponse], dependencies=[Depends(require_role_level(2))])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    days: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (KAPOLRI/KAPOLDA)"""
    logs = AuditService.get_all_logs(db, skip, limit, action, resource, days)
    return logs


@app.get("/api/audit-logs/user/{user_id}", response_model=List[AuditLogResponse])
async def get_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's audit logs (own or KAPOLRI/KAPOLDA)"""
    if current_user.id != user_id and current_user.role.level > 2:
        raise HTTPException(status_code=403, detail="Cannot view other user's logs")
    
    logs = AuditService.get_user_logs(db, user_id, skip, limit)
    return logs


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
