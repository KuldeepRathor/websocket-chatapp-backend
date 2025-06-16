from typing import Dict, List, Optional
from datetime import datetime
import json

class SimpleUser:
    def __init__(self, id: int, username: str, email: str, hashed_password: str):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = True
        self.is_online = False
        self.created_at = datetime.utcnow()

class SimpleRoom:
    def __init__(self, id: int, name: str, description: str, created_by: int, is_private: bool = False):
        self.id = id
        self.name = name
        self.description = description
        self.created_by = created_by
        self.is_private = is_private
        self.created_at = datetime.utcnow()

class SimpleMessage:
    def __init__(self, id: int, content: str, sender_id: int, room_id: int):
        self.id = id
        self.content = content
        self.sender_id = sender_id
        self.room_id = room_id
        self.created_at = datetime.utcnow()

class InMemoryStorage:
    def __init__(self):
        self.users: Dict[int, SimpleUser] = {}
        self.rooms: Dict[int, SimpleRoom] = {}
        self.messages: Dict[int, SimpleMessage] = {}
        self.user_counter = 1
        self.room_counter = 1
        self.message_counter = 1
    
    # User methods
    def create_user(self, username: str, email: str, hashed_password: str) -> SimpleUser:
        user = SimpleUser(self.user_counter, username, email, hashed_password)
        self.users[self.user_counter] = user
        self.user_counter += 1
        return user
    
    def get_user_by_username(self, username: str) -> Optional[SimpleUser]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[SimpleUser]:
        return self.users.get(user_id)
    
    # Room methods
    def create_room(self, name: str, description: str, created_by: int, is_private: bool = False) -> SimpleRoom:
        room = SimpleRoom(self.room_counter, name, description, created_by, is_private)
        self.rooms[self.room_counter] = room
        self.room_counter += 1
        return room
    
    def get_room_by_id(self, room_id: int) -> Optional[SimpleRoom]:
        return self.rooms.get(room_id)
    
    def get_public_rooms(self) -> List[SimpleRoom]:
        return [room for room in self.rooms.values() if not room.is_private]

# Global storage instance
storage = InMemoryStorage()
