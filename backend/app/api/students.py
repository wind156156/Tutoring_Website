from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.schemas import BaseResponse
from app.models import Assignment, AssignmentStudent, SubmissionFile, Student, Teacher, Binding

router = APIRouter(prefix="/students", tags=["学生"])


@router.get("/my-assignments", response_model=BaseResponse)
def my_assignments(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("student")),
):
    query = db.query(AssignmentStudent).filter(AssignmentStudent.student_id == user["id"])
    # We cannot use SQL for the overdue filter since it depends on the current time;
    # load all records first and filter/compute status in Python.
    all_items = query.order_by(AssignmentStudent.created_at.desc()).all()

    result = []
    for as_item in all_items:
        assignment = db.query(Assignment).filter(Assignment.id == as_item.assignment_id).first()
        teacher = db.query(Teacher).filter(Teacher.user_id == assignment.teacher_id).first() if assignment else None
        status = as_item.status
        # Dynamically mark as overdue if pending and past deadline
        if status == "pending" and assignment and assignment.due_at < datetime.utcnow():
            status = "overdue"
        # Apply status filter after computing dynamic status
        if status_filter and status != status_filter:
            continue
        result.append({
            "id": as_item.id,
            "assignment_id": as_item.assignment_id,
            "title": assignment.title if assignment else "",
            "subject": (assignment.subject if assignment else "") or "",
            "description": assignment.description if assignment else "",
            "content_images": json.loads(assignment.content_images) if assignment and assignment.content_images else [],
            "due_at": assignment.due_at.isoformat() if assignment and assignment.due_at else "",
            "max_score": float(assignment.max_score) if assignment else 100,
            "teacher_name": teacher.real_name if teacher else "",
            "status": status,
            "score": float(as_item.score) if as_item.score else None,
            "comment": as_item.comment,
            "submitted_at": as_item.submitted_at.isoformat() if as_item.submitted_at else None,
            "graded_at": as_item.graded_at.isoformat() if as_item.graded_at else None,
            "files": [
                {"url": sf.file_url, "name": sf.file_name}
                for sf in db.query(SubmissionFile).filter(
                    SubmissionFile.assignment_student_id == as_item.id
                ).all()
            ],
        })

    total = len(result)
    items = result[(page - 1) * page_size: page * page_size]

    return BaseResponse.ok(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/assignments/{assignment_id}", response_model=BaseResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("student")),
):
    as_item = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == user["id"],
    ).first()
    if not as_item:
        raise HTTPException(status_code=404, detail="作业不存在或未分配给你")

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    teacher = db.query(Teacher).filter(Teacher.user_id == assignment.teacher_id).first() if assignment else None

    # Teacher's attachment files (stored as URL strings, convert to objects)
    teacher_files = []
    if assignment and assignment.content_images:
        try:
            urls = json.loads(assignment.content_images)
            for u in urls:
                if isinstance(u, str):
                    teacher_files.append({"url": u, "name": u.split("/")[-1]})
                else:
                    teacher_files.append(u)
        except (json.JSONDecodeError, TypeError):
            pass

    # Student's submitted files
    student_files = [
        {"url": sf.file_url, "name": sf.file_name}
        for sf in db.query(SubmissionFile).filter(
            SubmissionFile.assignment_student_id == as_item.id
        ).all()
    ]

    return BaseResponse.ok(data={
        "id": as_item.id,
        "assignment_id": assignment_id,
        "title": assignment.title if assignment else "",
        "subject": (assignment.subject if assignment else "") or "",
        "description": assignment.description if assignment else "",
        "teacher_attachments": teacher_files,
        "due_at": assignment.due_at.isoformat() if assignment and assignment.due_at else "",
        "max_score": float(assignment.max_score) if assignment else 100,
        "teacher_name": teacher.real_name if teacher else "",
        "status": "overdue" if as_item.status == "pending" and assignment and assignment.due_at < datetime.utcnow() else as_item.status,
        "score": float(as_item.score) if as_item.score else None,
        "comment": as_item.comment,
        "student_submitted_files": student_files,
        "submitted_at": as_item.submitted_at.isoformat() if as_item.submitted_at else None,
        "graded_at": as_item.graded_at.isoformat() if as_item.graded_at else None,
    })


@router.post("/assignments/{assignment_id}/submit", response_model=BaseResponse)
def submit_assignment(
    assignment_id: int,
    files: list[dict] = Body(...),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("student")),
):
    as_item = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == user["id"],
    ).first()
    if not as_item:
        raise HTTPException(status_code=404, detail="作业不存在")

    if as_item.status == "graded":
        raise HTTPException(status_code=400, detail="该作业已批改，无法再次提交")

    # Check if overdue
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if assignment and assignment.due_at < datetime.utcnow() and as_item.status != "submitted":
        raise HTTPException(status_code=400, detail="作业已过期，无法提交")

    as_item.status = "submitted"
    as_item.submitted_at = datetime.utcnow()
    db.commit()

    # Save submission files
    for f in files:
        sf = SubmissionFile(
            assignment_student_id=as_item.id,
            file_url=f.get("url", ""),
            file_name=f.get("name", ""),
            file_size=f.get("size", 0),
        )
        db.add(sf)
    db.commit()

    return BaseResponse.ok(message="提交成功")


@router.get("/my-grades", response_model=BaseResponse)
def my_grades(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("student")),
):
    submissions = db.query(AssignmentStudent).filter(
        AssignmentStudent.student_id == user["id"],
        AssignmentStudent.score.isnot(None),
    ).all()

    total_score = sum(float(s.score or 0) for s in submissions)
    avg_score = total_score / len(submissions) if submissions else 0

    return BaseResponse.ok(data={
        "total_assignments": len(submissions),
        "total_score": total_score,
        "avg_score": avg_score,
        "grades": [
            {
                "id": s.id,
                "assignment_id": s.assignment_id,
                "title": (db.query(Assignment).filter(Assignment.id == s.assignment_id).first().title or ""),
                "score": float(s.score),
                "comment": s.comment,
                "graded_at": s.graded_at.isoformat() if s.graded_at else None,
            }
            for s in submissions
        ],
    })


@router.get("/my-teachers", response_model=BaseResponse)
def my_teachers(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("student")),
):
    bindings = db.query(Binding).filter(
        Binding.student_id == user["id"], Binding.status == "accepted"
    ).all()
    result = []
    for b in bindings:
        teacher = db.query(Teacher).filter(Teacher.user_id == b.teacher_id).first()
        if teacher:
            result.append({
                "id": teacher.user_id,
                "real_name": teacher.real_name,
                "gender": teacher.gender,
                "education": teacher.education,
                "title": teacher.title,
                "subject_tags": json.loads(teacher.subject_tags) if teacher.subject_tags else [],
                "experience_years": teacher.experience_years,
                "hourly_rate": float(teacher.hourly_rate),
                "city": teacher.city,
                "district": teacher.district,
                "rating_avg": float(teacher.rating_avg),
                "rating_count": teacher.rating_count,
                "is_verified": bool(teacher.is_verified),
                "bio": teacher.bio,
            })
    return BaseResponse.ok(data=result)
