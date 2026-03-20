from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class StatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"

class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="tasks")
    