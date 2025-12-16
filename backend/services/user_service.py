from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database.models import User, Role
from auth.security import get_password_hash


class UserService:
    """Service for user management operations"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_nrp(db: Session, nrp: str) -> Optional[User]:
        """Get user by NRP"""
        return db.query(User).filter(User.nrp == nrp).first()
    
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        Get list of users with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            role_id: Filter by role ID
            is_active: Filter by active status
        """
        query = db.query(User)
        
        if role_id is not None:
            query = query.filter(User.role_id == role_id)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search_users(db: Session, search: str, limit: int = 20) -> List[User]:
        """
        Search users by username, NRP, or full name
        
        Args:
            db: Database session
            search: Search term
            limit: Maximum results
        """
        search_pattern = f"%{search}%"
        return db.query(User).filter(
            or_(
                User.username.ilike(search_pattern),
                User.nrp.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    @staticmethod
    def create_user(
        db: Session,
        nrp: str,
        username: str,
        password: str,
        full_name: str,
        role_id: int,
        is_active: bool = True
    ) -> User:
        """
        Create new user
        
        Args:
            db: Database session
            nrp: User NRP
            username: Username
            password: Plain password
            full_name: Full name
            role_id: Role ID
            is_active: Active status
        """
        password_hash = get_password_hash(password)
        
        user = User(
            nrp=nrp,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role_id=role_id,
            is_active=is_active
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        full_name: Optional[str] = None,
        role_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Optional[User]:
        """
        Update user information
        
        Args:
            db: Database session
            user_id: User ID
            full_name: New full name
            role_id: New role ID
            is_active: New active status
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        if full_name is not None:
            user.full_name = full_name
        
        if role_id is not None:
            user.role_id = role_id
        
        if is_active is not None:
            user.is_active = is_active
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            db: Database session
            user_id: User ID
            new_password: New plain password
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete user account
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        
        return True
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """
        Deactivate user account
        
        Args:
            db: Database session
            user_id: User ID
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    def get_users_by_role_level(
        db: Session,
        max_level: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Get users with role level <= max_level
        
        Args:
            db: Database session
            max_level: Maximum role level (1=KAPOLRI, 2=KAPOLDA, 3=KAPOLRES)
            skip: Skip records
            limit: Limit results
        """
        return db.query(User).join(Role).filter(
            Role.level <= max_level
        ).offset(skip).limit(limit).all()
