from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import Dict
from datetime import datetime
import hashlib

# Import WebSocket components
from app.websocket.connection_manager import manager
from app.websocket.handlers.message_handler import (
    handle_send_message, 
    handle_join_room, 
    handle_leave_room,
    handle_typing_indicator
)

# Create FastAPI app
app = FastAPI(
    title="Chat App",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# Set up CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
users_db: Dict[str, dict] = {}
rooms_db: Dict[str, dict] = {
    "general": {
        "id": "general",
        "name": "General",
        "description": "General chat room",
        "created_at": datetime.utcnow().isoformat()
    },
    "random": {
        "id": "random",
        "name": "Random",
        "description": "Random discussions",
        "created_at": datetime.utcnow().isoformat()
    }
}

# Health check - important for deployment
@app.get("/")
async def root():
    return {"message": "Chat App API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "app": "Chat App",
        "active_connections": len(manager.active_connections),
        "rooms": list(rooms_db.keys())
    }

# Authentication endpoints
@app.post("/api/v1/auth/register")
async def register(username: str, email: str, password: str):
    if username in users_db:
        return {"error": "User already exists"}
    
    users_db[username] = {
        "id": len(users_db) + 1,
        "username": username,
        "email": email,
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "created_at": datetime.utcnow().isoformat()
    }
    return {"message": "User created successfully", "user_id": users_db[username]["id"]}

@app.post("/api/v1/auth/login")
async def login(username: str, password: str):
    if username not in users_db:
        return {"error": "User not found"}
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if users_db[username]["password_hash"] != password_hash:
        return {"error": "Invalid password"}
    
    return {"message": "Login successful", "token": f"fake-token-{username}", "user_id": username}

# Room endpoints
@app.get("/api/v1/rooms")
async def get_rooms():
    return {"rooms": list(rooms_db.values())}

@app.post("/api/v1/rooms")
async def create_room(name: str, description: str = ""):
    room_id = name.lower().replace(" ", "_")
    if room_id in rooms_db:
        return {"error": "Room already exists"}
    
    rooms_db[room_id] = {
        "id": room_id,
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }
    return {"message": "Room created successfully", "room": rooms_db[room_id]}

@app.get("/api/v1/users")
async def get_users():
    return {"users": list(users_db.keys())}

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Welcome {user_id}! You are now connected.",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = message_data.get("type")
            
            if message_type == "send_message":
                await handle_send_message(websocket, user_id, message_data)
            elif message_type == "join_room":
                await handle_join_room(websocket, user_id, message_data)
            elif message_type == "leave_room":
                await handle_leave_room(websocket, user_id, message_data)
            elif message_type == "typing":
                await handle_typing_indicator(websocket, user_id, message_data)
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
