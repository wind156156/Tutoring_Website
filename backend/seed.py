"""Seed script - create admin user and sample data."""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
import bcrypt

def hash_pwd(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
from app.models import User, Teacher, Student, Parent

def seed():
    db: Session = SessionLocal()

    # Create admin
    admin = db.query(User).filter(User.phone == "13800000001").first()
    if not admin:
        admin = User(
            phone="13800000001",
            password_hash=hash_pwd("admin123"),
            role="admin",
            nickname="管理员",
            status="active",
        )
        db.add(admin)
        db.flush()

    # Create test teacher
    test_teacher = db.query(User).filter(User.phone == "13800000002").first()
    if not test_teacher:
        test_teacher = User(
            phone="13800000002",
            password_hash=hash_pwd("teacher123"),
            role="teacher",
            nickname="李老师",
            status="active",
        )
        db.add(test_teacher)
        db.flush()

        teacher_profile = Teacher(
            user_id=test_teacher.id,
            real_name="李老师",
            education="硕士",
            title="高级教师",
            subject_tags=json.dumps(["数学", "物理"]),
            experience_years=10,
            hourly_rate=200,
            city="北京",
            district="海淀区",
            qualification_url="https://example.com/cert.jpg",
            bio="10年教龄，专注K12数理化辅导",
            is_verified=1,
        )
        db.add(teacher_profile)

    # Create test parent
    test_parent = db.query(User).filter(User.phone == "13800000003").first()
    if not test_parent:
        test_parent = User(
            phone="13800000003",
            password_hash=hash_pwd("parent123"),
            role="parent",
            nickname="张先生",
            status="active",
        )
        db.add(test_parent)
        db.flush()

        parent_profile = Parent(user_id=test_parent.id, real_name="张先生")
        db.add(parent_profile)

        # Create a student under this parent
        student = User(
            phone="13800000004",
            password_hash=hash_pwd("student123"),
            role="student",
            nickname="张小明",
            status="active",
        )
        db.add(student)
        db.flush()

        s_profile = Student(
            user_id=student.id,
            real_name="张小明",
            gender="male",
            grade="初二",
            school="北京实验二中",
            subjects=json.dumps(["数学", "英语"]),
            parent_id=test_parent.id,
        )
        db.add(s_profile)

    db.commit()
    db.close()
    print("Seed completed!")
    print("Admin: 13800000001 / admin123")
    print("Teacher: 13800000002 / teacher123")
    print("Parent: 13800000003 / parent123")
    print("Student: 13800000004 / student123")

if __name__ == "__main__":
    seed()
