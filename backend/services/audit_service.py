from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import AuditLog, User


class AuditService:
    """Service for audit logging operations"""
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry
        
        Args:
            db: Database session
            user_id: User who performed the action
            action: Action performed (login, logout, create, update, delete, etc)
            resource: Resource affected (auth, user, contact, message, etc)
            details: Additional details as JSON
            ip_address: IP address of user
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details or {},
            ip_address=ip_address
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        days: Optional[int] = None
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific user
        
        Args:
            db: Database session
            user_id: User ID
            skip: Skip records
            limit: Limit results
            action: Filter by action
            resource: Filter by resource
            days: Filter by last N days
        """
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource:
            query = query.filter(AuditLog.resource == resource)
        
        if days:
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AuditLog.timestamp >= since)
        
        return query.order_by(
            AuditLog.timestamp.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_logs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        days: Optional[int] = None
    ) -> tuple[List[AuditLog], int]:
        """
        Get all audit logs with optional filters
        
        Args:
            db: Database session
            skip: Skip records
            limit: Limit results
            action: Filter by action
            resource: Filter by resource
            days: Filter by last N days
            
        Returns:
            Tuple of (logs, total_count)
        """
        query = db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource:
            query = query.filter(AuditLog.resource == resource)
        
        if days:
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(AuditLog.timestamp >= since)
        
        total = query.count()
        logs = query.order_by(
            AuditLog.timestamp.desc()
        ).offset(skip).limit(limit).all()
        
        return logs, total
    
    @staticmethod
    def get_recent_activity(
        db: Session,
        hours: int = 24,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Get recent activity across all users
        
        Args:
            db: Database session
            hours: Last N hours
            limit: Limit results
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        return db.query(AuditLog).filter(
            AuditLog.timestamp >= since
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_action_count(
        db: Session,
        action: str,
        days: int = 30
    ) -> int:
        """
        Count occurrences of a specific action
        
        Args:
            db: Database session
            action: Action to count
            days: Within last N days
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        return db.query(AuditLog).filter(
            AuditLog.action == action,
            AuditLog.timestamp >= since
        ).count()
    
    @staticmethod
    def get_user_action_count(
        db: Session,
        user_id: int,
        action: str,
        days: int = 30
    ) -> int:
        """
        Count occurrences of a specific action by user
        
        Args:
            db: Database session
            user_id: User ID
            action: Action to count
            days: Within last N days
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == action,
            AuditLog.timestamp >= since
        ).count()
