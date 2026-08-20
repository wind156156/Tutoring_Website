from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.schemas import BaseResponse
from app.models import User, Teacher, Student, Binding, Announcement, Assignment, AssignmentStudent, AuditLog, Parent, SubmissionFile, Favorite, IMMessage

router = APIRouter(prefix="/admin", tags=["管理员"])


@router.get("/users", response_model=BaseResponse)
def list_users(
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if status:
        q = q.filter(User.status == status)

    total = q.count()
    items = q.order_by(User.id).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return BaseResponse.ok(data={
        "items": [
            {
                "id": u.id,
                "phone": u.phone,
                "nickname": u.nickname,
                "role": u.role,
                "status": u.status,
                "created_at": u.created_at.isoformat(),
            }
            for u in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.put("/users/{user_id}/status", response_model=BaseResponse)
def update_user_status(
    user_id: int,
    req: dict,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    new_status = req.get("status")
    if new_status not in ("active", "frozen", "pending"):
        raise HTTPException(status_code=400, detail="状态值无效")

    u.status = new_status
    db.commit()
    return BaseResponse.ok(message="操作成功")


# Minimum protected admin user IDs that cannot be deleted
_PROTECTED_ADMIN_IDS = {6}


@router.delete("/users/{user_id}", response_model=BaseResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    """Delete a user and all related data."""
    if user_id in _PROTECTED_ADMIN_IDS:
        raise HTTPException(status_code=403, detail="该管理员账号不可删除")

    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Delete child records in FK order
    db.query(IMMessage).filter(
        (IMMessage.sender_id == user_id) | (IMMessage.receiver_id == user_id)
    ).delete(synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete(synchronize_session=False)
    db.query(Favorite).filter(Favorite.user_id == user_id).delete(synchronize_session=False)
    db.query(Binding).filter(
        (Binding.teacher_id == user_id) | (Binding.student_id == user_id) | (Binding.parent_id == user_id)
    ).delete(synchronize_session=False)
    db.query(Assignment).filter(Assignment.teacher_id == user_id).delete(synchronize_session=False)
    db.query(AssignmentStudent).filter(AssignmentStudent.student_id == user_id).delete(synchronize_session=False)
    db.query(SubmissionFile).delete(synchronize_session=False)  # cascade from assignment_students
    db.query(Teacher).filter(Teacher.user_id == user_id).delete(synchronize_session=False)
    db.query(Student).filter(Student.user_id == user_id).delete(synchronize_session=False)
    db.query(Parent).filter(Parent.user_id == user_id).delete(synchronize_session=False)

    db.delete(u)
    db.commit()
    return BaseResponse.ok(message="删除成功")


@router.get("/teachers", response_model=BaseResponse)
def list_teachers_pending(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    query = db.query(Teacher).filter(
        Teacher.is_verified == 0,
        Teacher.rejected_at.is_(None),
    )
    # Pagination is done in Python to avoid DB-specific JSON functions
    all_items = query.order_by(Teacher.updated_at.desc()).all()
    result = []
    for t in all_items:
        parsed_tags = json.loads(t.subject_tags) if t.subject_tags else []
        if not parsed_tags:
            continue
        u = db.query(User).filter(User.id == t.user_id).first()
        result.append({
            "id": t.user_id,
            "phone": u.phone if u else "",
            "real_name": t.real_name,
            "education": t.education,
            "title": t.title,
            "subject_tags": json.loads(t.subject_tags) if t.subject_tags else [],
            "experience_years": t.experience_years,
            "hourly_rate": float(t.hourly_rate),
            "city": t.city,
            "qualification_url": t.qualification_url,
            "bio": t.bio,
            "created_at": u.created_at.isoformat() if u else "",
        })

    total = len(result)
    items = result[(page - 1) * page_size: page * page_size]

    return BaseResponse.ok(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.put("/teachers/{teacher_id}/verify", response_model=BaseResponse)
def verify_teacher(
    teacher_id: int,
    req: dict,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    t = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="老师不存在")

    action = req.get("action")
    if action == "approve":
        t.is_verified = 1
        u = db.query(User).filter(User.id == teacher_id).first()
        if u:
            u.status = "active"
            u.nickname = t.real_name
    elif action == "reject":
        t.is_verified = 0
        t.rejected_at = datetime.utcnow()
        u = db.query(User).filter(User.id == teacher_id).first()
        if u:
            u.status = "frozen"
    else:
        raise HTTPException(status_code=400, detail="action 必须是 approve 或 reject")

    db.commit()
    return BaseResponse.ok(message="操作成功")


@router.post("/announcements", response_model=BaseResponse)
def create_announcement(
    req: dict,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    announcement = Announcement(
        title=req["title"],
        content=req["content"],
        publish_from=datetime.fromisoformat(req["publish_from"]) if isinstance(req["publish_from"], str) else req["publish_from"],
        publish_to=datetime.fromisoformat(req["publish_to"]) if req.get("publish_to") and isinstance(req["publish_to"], str) else req.get("publish_to"),
        is_active=req.get("is_active", 1),
        created_by=admin["id"],
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    return BaseResponse.ok(data={"id": announcement.id}, message="公告创建成功")


@router.get("/announcements", response_model=BaseResponse)
def list_announcements(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    query = db.query(Announcement).order_by(Announcement.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return BaseResponse.ok(data={
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "publish_from": a.publish_from.isoformat(),
                "publish_to": a.publish_to.isoformat() if a.publish_to else None,
                "is_active": bool(a.is_active),
                "created_by": a.created_by,
                "created_at": a.created_at.isoformat(),
            }
            for a in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.put("/announcements/{announcement_id}", response_model=BaseResponse)
def update_announcement(
    announcement_id: int,
    req: dict,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="公告不存在")

    if req.get("title") is not None:
        a.title = req["title"]
    if req.get("content") is not None:
        a.content = req["content"]
    if req.get("is_active") is not None:
        a.is_active = req["is_active"]

    db.commit()
    return BaseResponse.ok(message="更新成功")


@router.get("/stats/overview", response_model=BaseResponse)
def overview_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
):
    total_users = db.query(User).count()
    total_teachers = db.query(Teacher).filter(Teacher.is_verified == 1).count()
    total_parents = db.query(User).filter(User.role == "parent").count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_assignments = db.query(Assignment).count()
    total_submissions = db.query(AssignmentStudent).count()
    total_bindings = db.query(Binding).filter(Binding.status == "accepted").count()

    return BaseResponse.ok(data={
        "total_users": total_users,
        "total_teachers": total_teachers,
        "total_parents": total_parents,
        "total_students": total_students,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "total_bindings": total_bindings,
    })
