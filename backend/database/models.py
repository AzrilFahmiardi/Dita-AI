"""
Database models for authentication and authorization.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Role(Base):
    """
    Role model for hierarchical permission system.
    Defines user roles with level-based hierarchy and flexible permissions.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    level = Column(Integer, nullable=False, index=True)
    permissions = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="role")


class User(Base):
    """
    User model for authentication.
    Stores user credentials, profile information, and role association.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nrp = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    user_contacts = relationship("UserContact", back_populates="user")

    def can_send_whatsapp(self) -> bool:
        """Check if user has permission to send WhatsApp messages."""
        if not self.role or not self.role.permissions:
            return False
        return self.role.permissions.get("send_whatsapp", False)

    def can_message_role_level(self, target_level: int) -> bool:
        """
        Check if user can message another user based on role hierarchy.
        Higher level (lower number) can message lower level (higher number).
        """
        if not self.role:
            return False
        return self.role.level <= target_level


class WhatsAppContact(Base):
    """
    WhatsApp contact model.
    Stores phone numbers and contact information for WhatsApp messaging.
    """
    __tablename__ = "whatsapp_contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user_contacts = relationship("UserContact", back_populates="contact")


class UserContact(Base):
    """
    Junction table for user-contact access control.
    Defines which contacts a user can send WhatsApp messages to.
    """
    __tablename__ = "user_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("whatsapp_contacts.id", ondelete="CASCADE"), nullable=False)
    can_send = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_contacts")
    contact = relationship("WhatsAppContact", back_populates="user_contacts")

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class Message(Base):
    """
    Message model for chat history and broadcasts.
    Stores all messages sent through the system.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipients = Column(JSON, nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, index=True)
    via_whatsapp = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", back_populates="sent_messages")


class AuditLog(Base):
    """
    Audit log model for security and compliance.
    Records all user actions for audit trail.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    resource = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="audit_logs")
