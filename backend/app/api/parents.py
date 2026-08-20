from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.core.security import hash_password
from app.schemas import BaseResponse
from app.models import User, Student, Parent, Binding, Teacher, Assignment, AssignmentStudent, SubmissionFile

router = APIRouter(prefix="/parents", tags=["家长"])


@router.get("/students", response_model=BaseResponse)
def list_students(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    students = db.query(Student).filter(Student.parent_id == user["id"]).all()
    return BaseResponse.ok(data=[
        {
            "id": s.user_id,
            "real_name": s.real_name,
            "gender": s.gender,
            "birth_year": s.birth_year,
            "grade": s.grade,
            "school": s.school,
            "subjects": json.loads(s.subjects) if s.subjects else [],
        }
        for s in students
    ])


@router.post("/students", response_model=BaseResponse)
def create_student(
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    phone = req.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="学生手机号不能为空")

    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    password = req.get("password", "123456")

    student_user = User(
        phone=phone,
        password_hash=hash_password(password),
        role="student",
        nickname=req.get("real_name", phone[:8]),
    )
    db.add(student_user)
    db.flush()

    student = Student(
        user_id=student_user.id,
        real_name=req.get("real_name", ""),
        gender=req.get("gender"),
        birth_year=req.get("birth_year"),
        grade=req.get("grade", ""),
        school=req.get("school", ""),
        subjects=json.dumps(req.get("subjects", [])) if req.get("subjects") else None,
        parent_id=user["id"],
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return BaseResponse.ok(data={
        "id": student.user_id,
        "real_name": student.real_name,
        "grade": student.grade,
        "school": student.school,
    }, message="学生添加成功")


@router.put("/students/{student_id}", response_model=BaseResponse)
def update_student(
    student_id: int,
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    student = db.query(Student).filter(
        Student.user_id == student_id,
        Student.parent_id == user["id"],
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    if req.get("real_name") is not None:
        student.real_name = req["real_name"]
        # 同步更新用户昵称，保证学生账号首页显示一致
        student_user = db.query(User).filter(User.id == student.user_id).first()
        if student_user:
            student_user.nickname = req["real_name"]
    if req.get("gender") is not None:
        student.gender = req["gender"]
    if req.get("birth_year") is not None:
        student.birth_year = req["birth_year"]
    if req.get("grade") is not None:
        student.grade = req["grade"]
    if req.get("school") is not None:
        student.school = req["school"]
    if req.get("subjects") is not None:
        student.subjects = json.dumps(req["subjects"])

    db.commit()
    return BaseResponse.ok(message="更新成功")


@router.delete("/students/{student_id}", response_model=BaseResponse)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    student = db.query(Student).filter(
        Student.user_id == student_id,
        Student.parent_id == user["id"],
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    student_user = db.query(User).filter(User.id == student_id).first()
    db.delete(student)
    if student_user:
        db.delete(student_user)
    db.commit()

    return BaseResponse.ok(message="删除成功")


@router.post("/bindings", response_model=BaseResponse)
def create_binding(
    req: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    teacher_id = req.get("teacher_id")
    student_id = req.get("student_id")
    reply_message = req.get("reply_message") or None

    if not teacher_id or not student_id:
        raise HTTPException(status_code=400, detail="老师ID和学生ID不能为空")

    student = db.query(Student).filter(
        Student.user_id == student_id,
        Student.parent_id == user["id"],
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在或不属于你")

    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="老师不存在")

    existing = db.query(Binding).filter(
        Binding.teacher_id == teacher_id,
        Binding.student_id == student_id,
        Binding.status == "accepted",
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学生和此老师已绑定")

    # Reuse rejected or expired binding instead of inserting (unique constraint)
    reused = db.query(Binding).filter(
        Binding.teacher_id == teacher_id,
        Binding.student_id == student_id,
        Binding.status.in_(["rejected", "expired"]),
    ).first()
    if reused:
        reused.status = "pending"
        reused.reply_message = reply_message
        reused.teacher_reply = None  # Clear previous teacher reply
        reused.expire_at = datetime.utcnow() + timedelta(days=7)
        db.commit()
        return BaseResponse.ok(data={"binding_id": reused.id}, message="绑定申请已发送")

    pending = db.query(Binding).filter(
        Binding.teacher_id == teacher_id,
        Binding.student_id == student_id,
        Binding.status == "pending",
    ).first()
    if pending:
        raise HTTPException(status_code=400, detail="已有待处理的绑定申请")

    binding = Binding(
        teacher_id=teacher_id,
        student_id=student_id,
        parent_id=user["id"],
        status="pending",
        reply_message=reply_message,
        expire_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(binding)
    db.commit()

    return BaseResponse.ok(data={"binding_id": binding.id}, message="绑定申请已发送")


@router.get("/bindings", response_model=BaseResponse)
def list_bindings(
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    bindings = db.query(Binding).filter(
        Binding.parent_id == user["id"]
    ).order_by(Binding.created_at.desc()).all()

    result = []
    for b in bindings:
        teacher = db.query(Teacher).filter(Teacher.user_id == b.teacher_id).first()
        student = db.query(Student).filter(Student.user_id == b.student_id).first()
        result.append({
            "id": b.id,
            "teacher_id": b.teacher_id,
            "teacher_name": teacher.real_name if teacher else "",
            "student_id": b.student_id,
            "student_name": student.real_name if student else "",
            "status": b.status,
            "reply_message": b.reply_message,
            "teacher_reply": b.teacher_reply,
            "created_at": b.created_at.isoformat(),
            "expire_at": b.expire_at.isoformat(),
        })

    return BaseResponse.ok(data=result)


def _format_assignment_student(as_item, db):
    """Format an AssignmentStudent record into a dict for parent viewing."""
    assignment = db.query(Assignment).filter(Assignment.id == as_item.assignment_id).first()
    teacher = db.query(Teacher).filter(Teacher.user_id == assignment.teacher_id).first() if assignment else None
    status = as_item.status
    if status == "pending" and assignment and assignment.due_at < datetime.utcnow():
        status = "overdue"
    files = [
        {"url": sf.file_url, "name": sf.file_name}
        for sf in db.query(SubmissionFile).filter(
            SubmissionFile.assignment_student_id == as_item.id
        ).all()
    ]
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

    return {
        "id": as_item.id,
        "assignment_id": as_item.assignment_id,
        "title": assignment.title if assignment else "",
        "subject": (assignment.subject if assignment else "") or "",
        "description": assignment.description if assignment else "",
        "teacher_attachments": teacher_files,
        "due_at": assignment.due_at.isoformat() if assignment and assignment.due_at else "",
        "max_score": float(assignment.max_score) if assignment else 100,
        "teacher_name": teacher.real_name if teacher else "",
        "status": status,
        "score": float(as_item.score) if as_item.score else None,
        "comment": as_item.comment,
        "submitted_at": as_item.submitted_at.isoformat() if as_item.submitted_at else None,
        "graded_at": as_item.graded_at.isoformat() if as_item.graded_at else None,
        "files": files,
    }


@router.get("/students/{student_id}/assignments", response_model=BaseResponse)
def get_student_assignments(
    student_id: int,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    student = db.query(Student).filter(
        Student.user_id == student_id,
        Student.parent_id == user["id"],
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在或不属于你")

    items = db.query(AssignmentStudent).filter(
        AssignmentStudent.student_id == student_id
    ).order_by(AssignmentStudent.created_at.desc()).all()

    result = [_format_assignment_student(as_item, db) for as_item in items]
    if status_filter:
        result = [r for r in result if r["status"] == status_filter]

    total = len(result)
    items = result[(page - 1) * page_size: page * page_size]
    return BaseResponse.ok(data={"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/students/{student_id}/assignments/{assignment_id}", response_model=BaseResponse)
def get_student_assignment_detail(
    student_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("parent")),
):
    student = db.query(Student).filter(
        Student.user_id == student_id,
        Student.parent_id == user["id"],
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在或不属于你")

    as_item = db.query(AssignmentStudent).filter(
        AssignmentStudent.assignment_id == assignment_id,
        AssignmentStudent.student_id == student_id,
    ).first()
    if not as_item:
        raise HTTPException(status_code=404, detail="作业不存在")

    return BaseResponse.ok(data=_format_assignment_student(as_item, db))
