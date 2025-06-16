import json
from datetime import datetime
from app.websocket.connection_manager import manager
from typing import Dict

# Simple message storage (in production, use database)
messages_storage: Dict[str, list] = {}

async def handle_send_message(websocket, user_id: str, data: dict):
    """Handle sending a message to a room"""
    try:
        room_id = data.get("room_id")
        content = data.get("content")
        
        if not room_id or not content:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "room_id and content are required"
            }))
            return
        
        # Create message
        message = {
            "id": len(messages_storage.get(room_id, [])) + 1,
            "type": "message",
            "content": content,
            "sender_id": user_id,
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store message
        if room_id not in messages_storage:
            messages_storage[room_id] = []
        messages_storage[room_id].append(message)
        
        # Broadcast to room
        await manager.broadcast_to_room(room_id, message)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error sending message: {str(e)}"
        }))

async def handle_join_room(websocket, user_id: str, data: dict):
    """Handle user joining a room"""
    try:
        room_id = data.get("room_id")
        if not room_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "room_id is required"
            }))
            return
        
        await manager.join_room(user_id, room_id)
        
        # Send recent messages to the user
        recent_messages = messages_storage.get(room_id, [])[-20:]  # Last 20 messages
        await websocket.send_text(json.dumps({
            "type": "room_joined",
            "room_id": room_id,
            "recent_messages": recent_messages
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error joining room: {str(e)}"
        }))

async def handle_leave_room(websocket, user_id: str, data: dict):
    """Handle user leaving a room"""
    try:
        room_id = data.get("room_id")
        if not room_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "room_id is required"
            }))
            return
        
        await manager.leave_room(user_id, room_id)
        
        await websocket.send_text(json.dumps({
            "type": "room_left",
            "room_id": room_id
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error leaving room: {str(e)}"
        }))

async def handle_typing_indicator(websocket, user_id: str, data: dict):
    """Handle typing indicator"""
    try:
        room_id = data.get("room_id")
        is_typing = data.get("is_typing", False)
        
        if not room_id:
            return
        
        # Broadcast typing indicator to room (excluding sender)
        await manager.broadcast_to_room(room_id, {
            "type": "typing_indicator",
            "user_id": user_id,
            "room_id": room_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error handling typing indicator: {str(e)}"
        }))
