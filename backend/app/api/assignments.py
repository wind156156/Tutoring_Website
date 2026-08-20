from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.schemas import BaseResponse
from app.models import Assignment, AssignmentStudent, SubmissionFile, Student, Teacher, Binding

router = APIRouter(prefix="/assignments", tags=["作业"])


@router.post("", response_model=BaseResponse)
def create_assignment(
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    student_ids = req.get("student_ids", [])
    if not student_ids:
        raise HTTPException(status_code=400, detail="必须指定至少一个学生")

    # Verify students are bound to this teacher
    bound_ids = {
        b.student_id for b in db.query(Binding).filter(
            Binding.teacher_id == user["id"],
            Binding.student_id.in_(student_ids),
            Binding.status == "accepted",
        ).all()
    }
    invalid = set(student_ids) - bound_ids
    if invalid:
        raise HTTPException(status_code=400, detail=f"以下学生未与该老师绑定: {list(invalid)}")

    due_at = req["due_at"]
    if not due_at or not isinstance(due_at, str) or due_at.strip() == '':
        raise HTTPException(status_code=400, detail="截止时间不能为空")
    try:
        due_at = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="截止时间格式错误，应为 yyyy-MM-dd HH:mm:ss")

    assignment = Assignment(
        teacher_id=user["id"],
        title=req["title"],
        subject=req.get("subject", ""),
        description=req.get("description"),
        content_images=json.dumps(req.get("content_images", [])) if req.get("content_images") else None,
        due_at=due_at,
        max_score=req.get("max_score", 100),
    )
    db.add(assignment)
    db.flush()

    for sid in student_ids:
        db.add(AssignmentStudent(assignment_id=assignment.id, student_id=sid, status="pending"))

    db.commit()
    db.refresh(assignment)
    return BaseResponse.ok(data={"id": assignment.id}, message="作业发布成功")


@router.get("", response_model=BaseResponse)
def list_assignments(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    total = db.query(Assignment).filter(Assignment.teacher_id == user["id"]).count()
    items = db.query(Assignment).filter(
        Assignment.teacher_id == user["id"]
    ).order_by(Assignment.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for a in items:
        sc = db.query(AssignmentStudent).filter(AssignmentStudent.assignment_id == a.id).count()
        gc = db.query(AssignmentStudent).filter(
            AssignmentStudent.assignment_id == a.id, AssignmentStudent.status == "graded"
        ).count()
        result.append({
            "id": a.id,
            "title": a.title,
            "subject": a.subject or "",
            "description": a.description,
            "content_images": json.loads(a.content_images) if a.content_images else [],
            "due_at": a.due_at.isoformat(),
            "max_score": float(a.max_score),
            "student_count": sc,
            "graded_count": gc,
            "created_at": a.created_at.isoformat(),
        })

    return BaseResponse.ok(data={"items": result, "total": total, "page": page, "page_size": page_size})


@router.get("/my-subjects", response_model=BaseResponse)
def my_subjects(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    """Get subjects from bound students for filtering."""
    bindings = db.query(Binding).filter(
        Binding.teacher_id == user["id"], Binding.status == "accepted"
    ).all()
    student_ids = [b.student_id for b in bindings]
    students = db.query(Student).filter(Student.user_id.in_(student_ids)).all()
    subjects = set()
    for s in students:
        if s.subjects:
            try:
                for subj in json.loads(s.subjects):
                    subjects.add(subj)
            except (json.JSONDecodeError, TypeError):
                pass
    return BaseResponse.ok(data=sorted(list(subjects)))


@router.get("/{assignment_id}", response_model=BaseResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, Assignment.teacher_id == user["id"]
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    submissions = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id
    ).all()

    result = []
    for as_item in submissions:
        student = db.query(Student).filter(Student.user_id == as_item.student_id).first()
        files = db.query(SubmissionFile).filter(
            SubmissionFile.assignment_student_id == as_item.id
        ).all()
        result.append({
            "id": as_item.id,
            "student_id": as_item.student_id,
            "student_name": student.real_name if student else "",
            "status": as_item.status,
            "score": float(as_item.score) if as_item.score else None,
            "comment": as_item.comment,
            "files": [{"url": f.file_url, "name": f.file_name} for f in files],
            "submitted_at": as_item.submitted_at.isoformat() if as_item.submitted_at else None,
        })

    return BaseResponse.ok(data={
        "id": assignment.id,
        "title": assignment.title,
        "subject": assignment.subject or "",
        "description": assignment.description,
        "content_images": json.loads(assignment.content_images) if assignment.content_images else [],
        "due_at": assignment.due_at.isoformat(),
        "max_score": float(assignment.max_score),
        "submissions": result,
    })


@router.put("/{assignment_id}", response_model=BaseResponse)
def update_assignment(
    assignment_id: int,
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, Assignment.teacher_id == user["id"]
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")
    if assignment.due_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="作业已截止，无法编辑")

    if req.get("title") is not None:
        assignment.title = req["title"]
    if req.get("subject") is not None:
        assignment.subject = req["subject"]
    if req.get("description") is not None:
        assignment.description = req["description"]
    if req.get("content_images") is not None:
        assignment.content_images = json.dumps(req["content_images"])
    if req.get("due_at") is not None:
        assignment.due_at = datetime.fromisoformat(req["due_at"])
    if req.get("max_score") is not None:
        assignment.max_score = req["max_score"]

    db.commit()
    return BaseResponse.ok(message="更新成功")


@router.delete("/{assignment_id}", response_model=BaseResponse)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, Assignment.teacher_id == user["id"]
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    db.delete(assignment)
    db.commit()
    return BaseResponse.ok(message="删除成功")


@router.post("/upload-attachment", response_model=BaseResponse)
async def upload_attachment(
    file: UploadFile = File(...),
    user: dict = Depends(require_role("teacher")),
):
    """Upload attachment image/file for assignment creation."""
    import os
    allowed_exts = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")
    await file.seek(0)

    safe_name = f"{user['id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    dest_path = os.path.join(upload_dir, safe_name)

    with open(dest_path, "wb") as f:
        f.write(content)

    url = f"/api/v1/files/served/{safe_name}"
    return BaseResponse.ok(data={"url": url, "name": file.filename})


@router.post("/{assignment_id}/grade/{student_id}", response_model=BaseResponse)
def grade_assignment(
    assignment_id: int,
    student_id: int,
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("teacher")),
):
    as_item = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == student_id,
    ).first()
    if not as_item:
        raise HTTPException(status_code=404, detail="作业提交不存在")
    if as_item.status == "pending":
        raise HTTPException(status_code=400, detail="学生尚未提交作业")

    as_item.score = req.get("score")
    as_item.comment = req.get("comment")
    as_item.status = "graded"
    as_item.graded_at = datetime.utcnow()
    db.commit()
    return BaseResponse.ok(message="批改成功")
