from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from config.db import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class TaskStatus(Enum):
        PENDING = "pending"
        IN_PROGRESS = "in-progress"
        COMPLETED = "completed"

        def __str__(self):
            return self.value

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"), 
        default=TaskStatus.PENDING, 
        nullable=False
    )
    checklist: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships - using string references instead of importing User
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee: Mapped["User"] = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")

    # SQLAlchemy validation - runs before database operations
    @validates('checklist')
    def validate_checklist(self, key, checklist):
        if checklist is not None:
            if not isinstance(checklist, dict):
                raise ValueError("Checklist must be a dictionary")
            
            items = checklist.get("items", [])
            if not isinstance(items, list):
                raise ValueError("Checklist items must be a list")
            
            if len(items) > 8:
                raise ValueError("Checklist cannot have more than 8 items")
            
            # Validate each item structure
            for i, item in enumerate(items):
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
            self.checklist = {"items": []}
        
        current_items = self.checklist.get("items", [])
        
        if len(current_items) >= 8:
            raise ValueError("Cannot add more than 8 items to checklist")
        
        # Check if item ID already exists
        if any(item["id"] == item_id for item in current_items):
            raise ValueError(f"Item with ID '{item_id}' already exists")
        
        new_item = {
            "id": item_id,
            "title": title.strip(),
            "completed": completed
        }
        
        current_items.append(new_item)
        self.checklist = {"items": current_items}  # Trigger validation
    
    def update_checklist_item(self, item_id: str, title: str = None, completed: bool = None):
        """Update an existing checklist item"""
        if self.checklist is None or "items" not in self.checklist:
            raise ValueError("No checklist items to update")
        
        items = self.checklist["items"]
        for item in items:
            if item["id"] == item_id:
                if title is not None:
                    item["title"] = title.strip()
                if completed is not None:
                    item["completed"] = completed
                
                # Trigger validation by reassigning
                self.checklist = {"items": items}
                return
        
        raise ValueError(f"Item with ID '{item_id}' not found")
    
    def remove_checklist_item(self, item_id: str):
        """Remove an item from the checklist"""
        if self.checklist is None or "items" not in self.checklist:
            raise ValueError("No checklist items to remove")
        
        items = self.checklist["items"]
        original_length = len(items)
        items = [item for item in items if item["id"] != item_id]
        
        if len(items) == original_length:
            raise ValueError(f"Item with ID '{item_id}' not found")
        
        self.checklist = {"items": items}

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    family_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50), default="member")  # 'admin' or 'member'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    created_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    assigned_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    