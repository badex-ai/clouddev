from datetime import datetime, timezone 
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean, Integer, func, CheckConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.orm.attributes import flag_modified
from config.db import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum
import uuid

class TaskStatus(Enum):
        initialised= "initialised"
        in_progress = "in-progress"
        completed = "completed"

        

class UserRole(Enum):
    admin = "admin"
    member = "member"

def utc_now() -> datetime:
    """Return timezone-aware datetime in UTC"""
    return datetime.now(timezone.utc)

  
class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(
        String(36), 
        unique=True, 
        index=True, 
        default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Changed to String(36) to match public_id data type
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.public_id"), nullable=False)
    assignee_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.public_id"), nullable=False)
    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("families.public_id"), nullable=False)
    
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"), 
        default=TaskStatus.initialised, 
        nullable=False
    )
    checklist: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships - using string references instead of importing User
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    family: Mapped["Family"] = relationship("Family", back_populates="tasks")

    __table_args__ = (
        # Note: This constraint needs to be updated since we're comparing strings now
        CheckConstraint('creator_id != assignee_id', name='creator_assignee_different'),
        CheckConstraint('due_date > created_at', name='due_date_after_creation'),
    )

    # SQLAlchemy validation - runs before database operations
    @validates('checklist')
    def validate_checklist(self, key, checklist):
        if checklist is not None:
            # 🔥 CHANGED: Now validating as a list instead of dict
            if not isinstance(checklist, list):
                raise ValueError("Checklist must be a list")
            
            # 🔥 CHANGED: Direct length check on checklist instead of items
            if len(checklist) > 8:
                raise ValueError("Checklist cannot have more than 8 items")
            
            # Validate each item structure
            for i, item in enumerate(checklist):
                if not isinstance(item, dict):
                    raise ValueError(f"Checklist item {i} must be a dictionary")
                
                required_fields = {"id", "title", "completed"}
                if not all(field in item for field in required_fields):
                    raise ValueError(f"Checklist item {i} missing required fields: {required_fields}")
                
                if not isinstance(item["completed"], bool):
                    raise ValueError(f"Checklist item {i} 'completed' must be a boolean")
                
                if not isinstance(item["title"], str) or len(item["title"].strip()) == 0:
                    raise ValueError(f"Checklist item {i} 'title' must be a non-empty string")
        
        return checklist

    # Convenience methods
    def add_checklist_item(self, item_id: str, title: str, completed: bool = False):
        """Add an item to the checklist"""
    
        if self.checklist is None:
            self.checklist = []
        
    
        if len(self.checklist) >= 8:
            raise ValueError("Cannot add more than 8 items to checklist")
        
        
        if any(item["id"] == item_id for item in self.checklist):
            raise ValueError(f"Item with ID '{item_id}' already exists")
        
        new_item = {
            "id": item_id,
            "title": title.strip(),
            "completed": completed
        }
        
        
        self.checklist.append(new_item)

        flag_modified(self, 'checklist')
        return self

    def update_checklist_item(self, item_id: str, title: str = None, completed: bool = None):
        """Update an existing checklist item"""
        if self.checklist is None:
            raise ValueError("No checklist items to update")
        
        
        for item in self.checklist:
            if item["id"] == item_id:
                if title is not None:
                    item["title"] = title.strip()
                if completed is not None:
                    item["completed"] = completed
                
                # No need to trigger validation by reassigning since we're modifying in place
                return
        
        raise ValueError(f"Item with ID '{item_id}' not found")

    def remove_checklist_item(self, item_id: str):
        """Remove an item from the checklist"""

        if self.checklist is None:
            raise ValueError("No checklist items to remove")
        
    
        original_length = len(self.checklist)
        self.checklist = [item for item in self.checklist if item["id"] != int(item_id)]
        
        if len(self.checklist) == original_length:
            raise ValueError(f"Item with ID '{item_id}' not found")
        flag_modified(self, 'checklist')
        return self
        
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(
        String(36), 
        unique=True, 
        index=True, 
        default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Changed to String(36) to match families.public_id
    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("families.public_id"), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="userrole"), default=UserRole.member, nullable=False)
    
    # Relationships
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    created_tasks: Mapped[Optional[List["Task"]]] = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    family: Mapped["Family"] = relationship("Family", back_populates="users")
    assigned_tasks: Mapped[Optional[List["Task"]]] = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
  
# Family model
class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(
        String(36), 
        unique=True, 
        index=True, 
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    users: Mapped[List["User"]] = relationship("User", back_populates="family")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="family")