from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import IMConversation, IMMessage, User

router = APIRouter()

# In-memory connection storage (use Redis for multi-worker production)
active_connections: Dict[int, Set[WebSocket]] = {}


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """WebSocket endpoint for real-time chat."""
    # Extract token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    # Validate token
    from app.core.security import decode_access_token
    token_data = decode_access_token(token)
    if not token_data or not token_data.user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = token_data.user_id
    await websocket.accept()

    # Register connection
    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "chat_message":
                # Broadcast to receiver
                receiver_id = msg.get("receiver_id")
                conversation_id = msg.get("conversation_id")
                content = msg.get("content", "")
                msg_type = msg.get("msg_type", "text")

                if not receiver_id or not conversation_id:
                    continue

                # Save to DB
                conv = db.query(IMConversation).filter(
                    IMConversation.id == conversation_id
                ).first()
                if not conv:
                    continue

                # Ensure sender is participant
                if conv.participant_1_id != user_id and conv.participant_2_id != user_id:
                    continue

                im_msg = IMMessage(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    msg_type=msg_type,
                    content=content,
                    is_read=0,
                    created_at=datetime.utcnow(),
                )
                db.add(im_msg)
                db.commit()
                db.refresh(im_msg)

                # Broadcast to receiver if online
                await _broadcast_to_user(receiver_id, {
                    "type": "chat_message",
                    "message_id": im_msg.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "conversation_id": conversation_id,
                    "msg_type": msg_type,
                    "content": content,
                    "created_at": im_msg.created_at.isoformat(),
                })

                # Send ack to sender
                await websocket.send_json({
                    "type": "ack",
                    "message_id": im_msg.id,
                })

    except WebSocketDisconnect:
        pass
    finally:
        # Clean up
        if user_id in active_connections:
            active_connections[user_id].discard(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]


async def _broadcast_to_user(user_id: int, payload: dict):
    """Send message to all WebSocket connections for a user."""
    conns = active_connections.get(user_id, set())
    for conn in conns:
        try:
            await conn.send_json(payload)
        except Exception:
            pass
