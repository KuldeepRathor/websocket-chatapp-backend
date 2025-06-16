from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Store active connections: user_id -> websocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Store room memberships: room_id -> set of user_ids
        self.room_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, user_id: str):
        """Disconnect a WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            # Remove from all rooms
            for room_id, users in self.room_connections.items():
                users.discard(user_id)
            print(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def join_room(self, user_id: str, room_id: str):
        """Add user to a room"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(user_id)
        
        # Notify others in the room
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    async def leave_room(self, user_id: str, room_id: str):
        """Remove user from a room"""
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(user_id)
            
            # Notify others in the room
            await self.broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user_id,
                "room_id": room_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except:
                # Connection is broken, remove it
                self.disconnect(user_id)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a room"""
        if room_id not in self.room_connections:
            return
        
        disconnected_users = []
        for user_id in self.room_connections[room_id]:
            if user_id == exclude_user:
                continue
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(json.dumps(message))
                except:
                    disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    def get_room_users(self, room_id: str) -> Set[str]:
        """Get all users in a room"""
        return self.room_connections.get(room_id, set())
    
    def get_user_rooms(self, user_id: str) -> Set[str]:
        """Get all rooms a user is in"""
        user_rooms = set()
        for room_id, users in self.room_connections.items():
            if user_id in users:
                user_rooms.add(room_id)
        return user_rooms

# Global connection manager instance
manager = ConnectionManager()
