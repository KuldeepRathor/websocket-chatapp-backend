from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseModel

class MessageType(PyEnum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"

class Message(BaseModel):
    __tablename__ = "messages"
    
    content = Column(String(1000), nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    
    # Relationships will be added later
    # sender = relationship("User", back_populates="sent_messages")
    # room = relationship("Room", back_populates="messages")
