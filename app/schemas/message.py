from pydantic import BaseModel
from datetime import datetime
from app.models.message import MessageType

class MessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT

class MessageCreate(MessageBase):
    room_id: int

class Message(MessageBase):
    id: int
    sender_id: int
    room_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
