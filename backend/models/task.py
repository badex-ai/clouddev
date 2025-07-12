from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config import Base

class Task(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    content: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Foreign key
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


