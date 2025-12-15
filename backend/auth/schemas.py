from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RoleSchema(BaseModel):
    id: int
    name: str
    level: int
    permissions: Dict[str, Any]

    class Config:
        from_attributes = True


class WhatsAppContactSchema(BaseModel):
    id: int
    name: str
    phone_number: str
    is_active: bool

    class Config:
        from_attributes = True


class UserContactSchema(BaseModel):
    contact: WhatsAppContactSchema
    can_send: bool

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    nrp: str
    username: str
    full_name: str
    is_active: bool
    role: RoleSchema
    contacts: List[UserContactSchema]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    recipients: List[str] = Field(..., min_items=1)
    message_type: str = Field(default="broadcast")
    via_whatsapp: bool = Field(default=False)


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipients: List[str]
    content: str
    message_type: str
    via_whatsapp: bool
    created_at: datetime

    class Config:
        from_attributes = True
