from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.db import Base
from models.task import Task   
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    family_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50), default="user")  # 'admin' or 'member'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    created_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    assigned_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")