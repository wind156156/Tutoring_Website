"""All database models for the tutoring platform.

Uses standard SQLAlchemy types that work with both MySQL and SQLite (dev).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text,
    UniqueConstraint, DECIMAL, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT as _TINYINT

from app.core.database import Base


# MySQL ENUM workaround: use VARCHAR with check constraints via events
def _set_mysql_enums(metadata):
    """Attach CHECK constraints for ENUM columns on MySQL."""
    for table in metadata.sorted_tables:
        for col in table.columns:
            if hasattr(col.type, '_enum_values'):
                pass  # handled by MySQL dialect


# ============ Users ============

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False, default="parent")
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False, default="")
    avatar = Column(String(500), nullable=False, default="")
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent_profile = relationship("Parent", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    announcements = relationship("Announcement", back_populates="creator")
    im_sender_messages = relationship("IMMessage", back_populates="sender", foreign_keys="IMMessage.sender_id")
    im_receiver_messages = relationship("IMMessage", back_populates="receiver", foreign_keys="IMMessage.receiver_id")


# ============ Parents ============

class Parent(Base):
    __tablename__ = "parents"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    real_name = Column(String(50), nullable=False, default="")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="parent_profile")
    students = relationship("Student", back_populates="parent", foreign_keys="Student.parent_id")
    bindings = relationship("Binding", back_populates="parent", foreign_keys="Binding.parent_id")


# ============ Teachers ============

class Teacher(Base):
    __tablename__ = "teachers"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    real_name = Column(String(50), nullable=False, default="")
    id_card = Column(String(20), unique=True, nullable=True)
    gender = Column(String(10), nullable=True)
    birth_year = Column(Integer, nullable=True)
    education = Column(String(100), nullable=False, default="")
    title = Column(String(100), nullable=False, default="")
    subject_tags = Column(Text, nullable=False, default='[]')
    experience_years = Column(Integer, nullable=False, default=0)
    hourly_rate = Column(DECIMAL(8, 2), nullable=False, default=0)
    city = Column(String(50), nullable=False, default="")
    district = Column(String(50), nullable=False, default="")
    qualification_url = Column(String(500), nullable=False, default="")
    bio = Column(Text, nullable=False, default="")
    rating_avg = Column(DECIMAL(3, 2), nullable=False, default=0)
    rating_count = Column(Integer, nullable=False, default=0)
    completed_orders = Column(Integer, nullable=False, default=0)
    is_verified = Column(Integer, nullable=False, default=0)
    rejected_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="teacher_profile")
    bindings_as_teacher = relationship(
        "Binding", back_populates="teacher", foreign_keys="Binding.teacher_id"
    )
    assignments = relationship("Assignment", back_populates="teacher_obj", cascade="all, delete-orphan")
    favorites_as_teacher = relationship("Favorite", back_populates="teacher")


# ============ Students ============

class Student(Base):
    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    real_name = Column(String(50), nullable=False, default="")
    gender = Column(String(10), nullable=True)
    birth_year = Column(Integer, nullable=True)
    grade = Column(String(20), nullable=False, default="")
    school = Column(String(100), nullable=False, default="")
    subjects = Column(Text, nullable=True)  # JSON array
    parent_id = Column(Integer, ForeignKey("parents.user_id"), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="student_profile")
    parent = relationship("Parent", back_populates="students", foreign_keys=[parent_id])
    bindings_as_student = relationship(
        "Binding", back_populates="student", foreign_keys="Binding.student_id"
    )
    assignment_submissions = relationship("AssignmentStudent", back_populates="student_obj", cascade="all, delete-orphan")


# ============ Bindings ============

class Binding(Base):
    __tablename__ = "teacher_student_bindings"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.user_id"), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    reply_message = Column(Text, nullable=True)  # Parent's original message
    teacher_reply = Column(Text, nullable=True)  # Teacher's reply when accepting/rejecting
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expire_at = Column(DateTime, nullable=False)

    teacher = relationship("Teacher", back_populates="bindings_as_teacher", foreign_keys=[teacher_id])
    student = relationship("Student", back_populates="bindings_as_student", foreign_keys=[student_id])
    parent = relationship("Parent", back_populates="bindings", foreign_keys=[parent_id])

    __table_args__ = (
        UniqueConstraint("teacher_id", "student_id", name="uq_teacher_student"),
        Index("idx_teacher_status", "teacher_id", "status"),
        Index("idx_parent_bindings", "parent_id", "status"),
    )


# ============ Assignments ============

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    subject = Column(String(50), nullable=False, default="")
    description = Column(Text, nullable=True)
    content_images = Column(Text, nullable=True)  # JSON array
    due_at = Column(DateTime, nullable=False)
    max_score = Column(DECIMAL(6, 2), nullable=False, default=100)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher_obj = relationship("Teacher", back_populates="assignments", foreign_keys=[teacher_id])
    students = relationship("AssignmentStudent", back_populates="assignment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_teacher_created", "teacher_id", "created_at"),
        Index("idx_due", "due_at"),
    )


class AssignmentStudent(Base):
    __tablename__ = "assignment_students"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.user_id"), nullable=False)
    score = Column(DECIMAL(6, 2), nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    submitted_at = Column(DateTime, nullable=True)
    graded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    assignment = relationship("Assignment", back_populates="students")
    student_obj = relationship("Student", back_populates="assignment_submissions")
    submissions = relationship("SubmissionFile", back_populates="assignment_student", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_assignment_status", "assignment_id", "status"),
    )


class SubmissionFile(Base):
    __tablename__ = "submission_files"

    id = Column(Integer, primary_key=True, index=True)
    assignment_student_id = Column(Integer, ForeignKey("assignment_students.id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    assignment_student = relationship("AssignmentStudent", back_populates="submissions")

    __table_args__ = (
        Index("idx_as", "assignment_student_id"),
    )


# ============ Favorites ============

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="favorites_as_teacher")

    __table_args__ = (
        UniqueConstraint("user_id", "teacher_id", name="uq_user_teacher"),
    )


# ============ Announcements ============

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    publish_from = Column(DateTime, nullable=False)
    publish_to = Column(DateTime, nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    creator = relationship("User", back_populates="announcements")

    __table_args__ = (
        Index("idx_active_publish", "is_active", "publish_from", "publish_to"),
    )


# ============ Audit Logs ============

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False, default="")
    entity_id = Column(Integer, nullable=True)
    detail = Column(Text, nullable=True)  # JSON
    ip = Column(String(45), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_user_action", "user_id", "action"),
        Index("idx_created", "created_at"),
    )


# ============ IM (Instant Messaging) ============

class IMConversation(Base):
    __tablename__ = "im_conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_key = Column(String(64), nullable=False, unique=True, index=True)
    participant_1_id = Column(Integer, nullable=False)
    participant_2_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("IMMessage", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_p1_p2", "participant_1_id", "participant_2_id"),
    )


class IMMessage(Base):
    __tablename__ = "im_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("im_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    msg_type = Column(String(20), nullable=False, default="text")
    content = Column(Text, nullable=False)
    is_read = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    conversation = relationship("IMConversation", back_populates="messages")
    sender = relationship("User", back_populates="im_sender_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="im_receiver_messages", foreign_keys=[receiver_id])

    __table_args__ = (
        Index("idx_conv_time", "conversation_id", "created_at"),
        Index("idx_sender", "sender_id", "created_at"),
        Index("idx_receiver_unread", "receiver_id", "is_read", "created_at"),
    )
