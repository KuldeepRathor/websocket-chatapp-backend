from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseModel

class MemberRole(PyEnum):
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"

class RoomMember(BaseModel):
    __tablename__ = "room_members"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
    joined_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="room_memberships")
    room = relationship("Room", back_populates="members")