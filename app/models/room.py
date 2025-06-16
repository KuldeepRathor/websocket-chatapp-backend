from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Room(BaseModel):
    __tablename__ = "rooms"
    
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    is_private = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships will be added later
    # creator = relationship("User", foreign_keys=[created_by])
    # messages = relationship("Message", back_populates="room")
    # members = relationship("RoomMember", back_populates="room")
