from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoomBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None

class Room(RoomBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
