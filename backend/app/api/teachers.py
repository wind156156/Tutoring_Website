from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from sqlalchemy import func
from app.schemas import BaseResponse
from app.models import User, Teacher, Student, Binding, Favorite, Parent

router = APIRouter(prefix="/teachers", tags=["老师"])


def _teacher_to_dict(t: Teacher, db: Session, current_user_id: Optional[int]) -> dict:
    parsed_tags = json.loads(t.subject_tags) if t.subject_tags else []
    if t.is_verified == 1:
        review_status = "approved"
    elif not t.rejected_at and parsed_tags:
        review_status = "pending"
    elif t.rejected_at:
        review_status = "rejected"
    else:
        review_status = "none"
    data = {
        "id": t.user_id,
        "real_name": t.real_name,
        "gender": t.gender,
        "education": t.education,
        "title": t.title,
        "subject_tags": parsed_tags,
        "experience_years": t.experience_years,
        "hourly_rate": float(t.hourly_rate),
        "city": t.city,
        "district": t.district,
        "qualification_url": t.qualification_url,
        "bio": t.bio,
        "rating_avg": float(t.rating_avg),
        "rating_count": t.rating_count,
        "completed_orders": t.completed_orders,
        "is_verified": bool(t.is_verified),
        "review_status": review_status,
    }
    if current_user_id:
        fav = db.query(Favorite).filter(
            Favorite.user_id == current_user_id,
            Favorite.teacher_id == t.user_id,
        ).first()
        data["is_favorited"] = bool(fav)
    else:
        data["is_favorited"] = False
    return data


# --- Public endpoints (must come BEFORE parameterized routes) ---

@router.get("/my-profile", response_model=BaseResponse)
def my_profile(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    """Get current teacher's profile."""
    teacher = db.query(Teacher).filter(Teacher.user_id == user["id"]).first()
    if not teacher:
        return BaseResponse.ok(data=None, message="资料未填写")
    return BaseResponse.ok(data=_teacher_to_dict(teacher, db, user.get("id")))


@router.post("/my-profile", response_model=BaseResponse)
def create_or_update_profile(
    req: dict = Body(...),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    """Create or update teacher profile."""
    teacher = db.query(Teacher).filter(Teacher.user_id == user["id"]).first()
    if not teacher:
        teacher = Teacher(user_id=user["id"])
        db.add(teacher)

    if req.get("real_name") is not None:
        teacher.real_name = req["real_name"]
    if req.get("gender") is not None:
        teacher.gender = req["gender"]
    if req.get("birth_year") is not None:
        teacher.birth_year = req["birth_year"]
    if req.get("education") is not None:
        teacher.education = req["education"]
    if req.get("title") is not None:
        teacher.title = req["title"]
    if req.get("subject_tags") is not None:
        teacher.subject_tags = json.dumps(req["subject_tags"])
    if req.get("experience_years") is not None:
        teacher.experience_years = req["experience_years"]
    if req.get("hourly_rate") is not None:
        teacher.hourly_rate = req["hourly_rate"]
    if req.get("city") is not None:
        teacher.city = req["city"]
    if req.get("district") is not None:
        teacher.district = req["district"]
    if req.get("qualification_url") is not None:
        teacher.qualification_url = req["qualification_url"]
    if req.get("bio") is not None:
        teacher.bio = req["bio"]

    db.commit()
    db.refresh(teacher)

    # Sync user nickname with real_name when it changes
    u = db.query(User).filter(User.id == user["id"]).first()
    if u and req.get("real_name") is not None:
        u.nickname = req["real_name"]
        db.commit()

    # Clear rejection when resubmitting, or re-queue after approval
    if teacher.rejected_at is not None:
        teacher.rejected_at = None
    elif teacher.is_verified == 1:
        teacher.is_verified = 0
    db.commit()

    return BaseResponse.ok(data=_teacher_to_dict(teacher, db, user.get("id")), message="资料已保存")


@router.get("", response_model=BaseResponse)
def list_teachers(
    subject: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    min_rate: Optional[float] = Query(None),
    max_rate: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Teacher).filter(Teacher.is_verified == 1)
    if subject:
        query = query.filter(func.json_contains(Teacher.subject_tags, func.json_quote(subject)))
    if city:
        query = query.filter(Teacher.city == city)
    if min_rate is not None:
        query = query.filter(Teacher.hourly_rate >= min_rate)
    if max_rate is not None:
        query = query.filter(Teacher.hourly_rate <= max_rate)
    if min_rating is not None:
        query = query.filter(Teacher.rating_avg >= min_rating)
    total = query.count()
    items = query.order_by(Teacher.rating_avg.desc(), Teacher.hourly_rate.asc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return BaseResponse.ok(data={
        "items": [_teacher_to_dict(t, db, user.get("id")) for t in items],
        "total": total, "page": page, "page_size": page_size,
    })


# --- Authenticated teacher endpoints (specific paths first) ---

@router.get("/my-bindings", response_model=BaseResponse)
def my_bindings(
    status_filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    query = db.query(Binding).filter(Binding.teacher_id == user["id"])
    if status_filter:
        query = query.filter(Binding.status == status_filter)
    total = query.count()
    items = query.order_by(Binding.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    result = []
    for b in items:
        student = db.query(Student).filter(Student.user_id == b.student_id).first()
        parent = db.query(Parent).filter(Parent.user_id == b.parent_id).first()
        result.append({
            "id": b.id, "student_id": b.student_id,
            "student_name": student.real_name if student else "",
            "parent_id": b.parent_id,
            "parent_name": parent.real_name if parent else "",
            "status": b.status,
            "reply_message": b.reply_message,  # Parent's original message
            "teacher_reply": b.teacher_reply,  # Teacher's reply
            "created_at": b.created_at.isoformat(),
            "expire_at": b.expire_at.isoformat(),
        })
    return BaseResponse.ok(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.post("/bindings/{binding_id}/reply", response_model=BaseResponse)
def reply_binding(
    binding_id: int,
    action: str,
    teacher_reply: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    binding = db.query(Binding).filter(
        Binding.id == binding_id, Binding.teacher_id == user["id"]
    ).first()
    if not binding:
        raise HTTPException(status_code=404, detail="绑定申请不存在")
    if binding.status != "pending":
        raise HTTPException(status_code=400, detail="该申请已处理")
    if action == "accept":
        binding.status = "accepted"
    elif action == "reject":
        binding.status = "rejected"
    else:
        raise HTTPException(status_code=400, detail="action 必须是 accept 或 reject")
    # Only store teacher's reply when explicitly provided; don't overwrite parent's message
    if teacher_reply is not None:
        binding.teacher_reply = teacher_reply
    db.commit()
    return BaseResponse.ok(message="操作成功")


@router.get("/my-students", response_model=BaseResponse)
def my_students(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    bindings = db.query(Binding).filter(
        Binding.teacher_id == user["id"], Binding.status == "accepted"
    ).all()
    result = []
    for b in bindings:
        student = db.query(Student).filter(Student.user_id == b.student_id).first()
        if student:
            result.append({
                "id": student.user_id, "real_name": student.real_name,
                "gender": student.gender, "grade": student.grade,
                "school": student.school,
                "subjects": json.loads(student.subjects) if student.subjects else [],
            })
    return BaseResponse.ok(data=result)


@router.get("/my-favorites", response_model=BaseResponse)
def my_favorites(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user["role"] not in ("teacher", "parent", "student"):
        return BaseResponse.ok(data=[])
    favs = db.query(Favorite).filter(Favorite.user_id == user["id"]).all()
    teacher_ids = [f.teacher_id for f in favs]
    if not teacher_ids:
        return BaseResponse.ok(data=[])
    teachers = db.query(Teacher).filter(Teacher.user_id.in_(teacher_ids)).all()
    return BaseResponse.ok(data=[
        {"id": t.user_id, "real_name": t.real_name, "subject_tags": json.loads(t.subject_tags) if t.subject_tags else []}
        for t in teachers
    ])


@router.post("/favorite/{teacher_id}", response_model=BaseResponse)
def toggle_favorite(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher", "parent", "student")),
):
    existing = db.query(Favorite).filter(
        Favorite.user_id == user["id"], Favorite.teacher_id == teacher_id
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return BaseResponse.ok(data={"is_favorited": False}, message="已取消收藏")
    else:
        fav = Favorite(user_id=user["id"], teacher_id=teacher_id)
        db.add(fav)
        db.commit()
        return BaseResponse.ok(data={"is_favorited": True}, message="收藏成功")


# --- Parameterized endpoints (catch-all must come LAST) ---

@router.get("/{teacher_id}", response_model=BaseResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    t = db.query(Teacher).filter(Teacher.user_id == teacher_id, Teacher.is_verified == 1).first()
    if not t:
        raise HTTPException(status_code=404, detail="老师不存在")
    return BaseResponse.ok(data=_teacher_to_dict(t, db, user.get("id")))
