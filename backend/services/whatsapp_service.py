from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import WhatsAppContact, UserContact, User, Message


class WhatsAppService:
    """Service for WhatsApp contact and messaging operations"""
    
    @staticmethod
    def get_contact_by_id(db: Session, contact_id: int) -> Optional[WhatsAppContact]:
        """Get WhatsApp contact by ID"""
        return db.query(WhatsAppContact).filter(WhatsAppContact.id == contact_id).first()
    
    @staticmethod
    def get_contact_by_phone(db: Session, phone_number: str) -> Optional[WhatsAppContact]:
        """Get WhatsApp contact by phone number"""
        return db.query(WhatsAppContact).filter(
            WhatsAppContact.phone_number == phone_number
        ).first()
    
    @staticmethod
    def get_all_contacts(
        db: Session,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WhatsAppContact]:
        """
        Get all WhatsApp contacts
        
        Args:
            db: Database session
            is_active: Filter by active status
            skip: Skip records
            limit: Limit results
        """
        query = db.query(WhatsAppContact)
        
        if is_active is not None:
            query = query.filter(WhatsAppContact.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_contacts(db: Session, user_id: int) -> List[UserContact]:
        """
        Get all WhatsApp contacts assigned to a user
        
        Args:
            db: Database session
            user_id: User ID
        """
        return db.query(UserContact).filter(UserContact.user_id == user_id).all()
    
    @staticmethod
    def create_contact(
        db: Session,
        name: str,
        phone_number: str,
        is_active: bool = True
    ) -> WhatsAppContact:
        """
        Create new WhatsApp contact
        
        Args:
            db: Database session
            name: Contact name
            phone_number: Phone number
            is_active: Active status
        """
        contact = WhatsAppContact(
            name=name,
            phone_number=phone_number,
            is_active=is_active
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        return contact
    
    @staticmethod
    def update_contact(
        db: Session,
        contact_id: int,
        name: Optional[str] = None,
        phone_number: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[WhatsAppContact]:
        """
        Update WhatsApp contact
        
        Args:
            db: Database session
            contact_id: Contact ID
            name: New name
            phone_number: New phone number
            is_active: New active status
        """
        contact = db.query(WhatsAppContact).filter(
            WhatsAppContact.id == contact_id
        ).first()
        
        if not contact:
            return None
        
        if name is not None:
            contact.name = name
        
        if phone_number is not None:
            contact.phone_number = phone_number
        
        if is_active is not None:
            contact.is_active = is_active
        
        contact.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(contact)
        
        return contact
    
    @staticmethod
    def delete_contact(db: Session, contact_id: int) -> bool:
        """
        Delete WhatsApp contact
        
        Args:
            db: Database session
            contact_id: Contact ID
            
        Returns:
            True if deleted, False if not found
        """
        contact = db.query(WhatsAppContact).filter(
            WhatsAppContact.id == contact_id
        ).first()
        
        if not contact:
            return False
        
        # Delete related user_contacts first
        db.query(UserContact).filter(UserContact.contact_id == contact_id).delete()
        
        # Then delete the contact
        db.delete(contact)
        db.commit()
        
        return True
    
    @staticmethod
    def assign_contact_to_user(
        db: Session,
        user_id: int,
        contact_id: int,
        can_send: bool = True
    ) -> Optional[UserContact]:
        """
        Assign WhatsApp contact to user
        
        Args:
            db: Database session
            user_id: User ID
            contact_id: Contact ID
            can_send: Permission to send messages
        """
        existing = db.query(UserContact).filter(
            UserContact.user_id == user_id,
            UserContact.contact_id == contact_id
        ).first()
        
        if existing:
            existing.can_send = can_send
            db.commit()
            db.refresh(existing)
            return existing
        
        user_contact = UserContact(
            user_id=user_id,
            contact_id=contact_id,
            can_send=can_send
        )
        
        db.add(user_contact)
        db.commit()
        db.refresh(user_contact)
        
        return user_contact
    
    @staticmethod
    def remove_contact_from_user(
        db: Session,
        user_id: int,
        contact_id: int
    ) -> bool:
        """
        Remove WhatsApp contact assignment from user
        
        Args:
            db: Database session
            user_id: User ID
            contact_id: Contact ID
        """
        user_contact = db.query(UserContact).filter(
            UserContact.user_id == user_id,
            UserContact.contact_id == contact_id
        ).first()
        
        if not user_contact:
            return False
        
        db.delete(user_contact)
        db.commit()
        
        return True
    
    @staticmethod
    def can_user_send_to_contact(
        db: Session,
        user_id: int,
        contact_id: int
    ) -> bool:
        """
        Check if user can send messages to a contact
        
        Args:
            db: Database session
            user_id: User ID
            contact_id: Contact ID
        """
        user_contact = db.query(UserContact).filter(
            UserContact.user_id == user_id,
            UserContact.contact_id == contact_id,
            UserContact.can_send == True
        ).first()
        
        return user_contact is not None
    
    @staticmethod
    def create_message(
        db: Session,
        sender_id: int,
        recipients: List[str],
        content: str,
        message_type: str = "broadcast",
        via_whatsapp: bool = False
    ) -> Message:
        """
        Create a message record
        
        Args:
            db: Database session
            sender_id: Sender user ID
            recipients: List of recipient identifiers
            content: Message content
            message_type: Type of message (broadcast, direct, etc)
            via_whatsapp: Whether sent via WhatsApp
        """
        message = Message(
            sender_id=sender_id,
            recipients=recipients,
            content=content,
            message_type=message_type,
            via_whatsapp=via_whatsapp
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message
    
    @staticmethod
    def get_user_messages(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages sent by a user
        
        Args:
            db: Database session
            user_id: User ID
            skip: Skip records
            limit: Limit results
        """
        return db.query(Message).filter(
            Message.sender_id == user_id
        ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
