from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.schemas import BaseResponse
from app.models import Announcement, IMConversation, IMMessage, Student, User

router = APIRouter(prefix="", tags=["公共接口"])


@router.get("/announcements", response_model=BaseResponse)
def list_active_announcements(
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    items = db.query(Announcement).filter(
        Announcement.is_active == 1,
        Announcement.publish_from <= now,
        Announcement.publish_to >= now,
    ).order_by(Announcement.created_at.desc()).all()

    return BaseResponse.ok(data=[
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "publish_from": a.publish_from.isoformat(),
            "created_at": a.created_at.isoformat(),
        }
        for a in items
    ])


@router.get("/subjects", response_model=BaseResponse)
def get_subjects(
    db: Session = Depends(get_db),
):
    # Simple subject list
    subjects = ["语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理", "科学", "编程", "美术", "音乐", "体育"]
    return BaseResponse.ok(data=subjects)


# ============ IM Module ============

im_router = APIRouter(prefix="/im", tags=["IM聊天"])


@im_router.get("/conversations", response_model=BaseResponse)
def list_conversations(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get conversations where user is a participant."""
    conversations = db.query(IMConversation).filter(
        (IMConversation.participant_1_id == user["id"]) |
        (IMConversation.participant_2_id == user["id"])
    ).order_by(IMConversation.updated_at.desc()).all()

    result = []
    for c in conversations:
        # Get last message
        last_msg = db.query(IMMessage).filter(
            IMMessage.conversation_id == c.id
        ).order_by(IMMessage.created_at.desc()).first()

        # Get unread count
        other_id = c.participant_2_id if c.participant_1_id == user["id"] else c.participant_1_id
        unread = db.query(IMMessage).filter(
            IMMessage.conversation_id == c.id,
            IMMessage.receiver_id == user["id"],
            IMMessage.is_read == 0,
        ).count()

        result.append({
            "id": c.id,
            "conversation_key": c.conversation_key,
            "participant_1_id": c.participant_1_id,
            "participant_2_id": c.participant_2_id,
            "unread_count": unread,
            "last_message": {
                "id": last_msg.id,
                "sender_id": last_msg.sender_id,
                "msg_type": last_msg.msg_type,
                "content": last_msg.content,
                "created_at": last_msg.created_at.isoformat(),
            } if last_msg else None,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        })

    return BaseResponse.ok(data=result)


@im_router.get("/conversations/{conv_id}/messages", response_model=BaseResponse)
def get_messages(
    conv_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    conv = db.query(IMConversation).filter(IMConversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")

    # Check user is participant
    if conv.participant_1_id != user["id"] and conv.participant_2_id != user["id"]:
        raise HTTPException(status_code=403, detail="无权访问此会话")

    total = db.query(IMMessage).filter(IMMessage.conversation_id == conv_id).count()
    messages = db.query(IMMessage).filter(
        IMMessage.conversation_id == conv_id
    ).order_by(IMMessage.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    # Mark as read
    db.query(IMMessage).filter(
        IMMessage.conversation_id == conv_id,
        IMMessage.receiver_id == user["id"],
        IMMessage.is_read == 0,
    ).update({"is_read": 1}, synchronize_session=False)
    db.commit()

    return BaseResponse.ok(data={
        "items": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "msg_type": m.msg_type,
                "content": m.content,
                "is_read": bool(m.is_read),
                "created_at": m.created_at.isoformat(),
            }
            for m in reversed(messages)
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@im_router.get("/unread-count", response_model=BaseResponse)
def unread_count(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    count = db.query(IMMessage).filter(
        IMMessage.receiver_id == user["id"],
        IMMessage.is_read == 0,
    ).count()
    return BaseResponse.ok(data={"count": count})


@im_router.post("/conversations", response_model=BaseResponse)
def create_conversation(
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    other_id = req.get("other_id")
    if not other_id:
        raise HTTPException(status_code=400, detail="对方ID不能为空")

    # Check if conversation already exists
    existing = db.query(IMConversation).filter(
        ((IMConversation.participant_1_id == user["id"]) & (IMConversation.participant_2_id == other_id)) |
        ((IMConversation.participant_1_id == other_id) & (IMConversation.participant_2_id == user["id"]))
    ).first()

    if existing:
        return BaseResponse.ok(data={"id": existing.id, "conversation_key": existing.conversation_key})

    # Generate unique key
    key = f"conv_{min(user['id'], other_id)}_{max(user['id'], other_id)}"
    conv = IMConversation(
        conversation_key=key,
        participant_1_id=min(user["id"], other_id),
        participant_2_id=max(user["id"], other_id),
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    return BaseResponse.ok(data={"id": conv.id, "conversation_key": conv.conversation_key})
