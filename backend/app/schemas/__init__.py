from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class BaseResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None

    @classmethod
    def ok(cls, data=None, message: str = "success"):
        return cls(code=0, message=message, data=data)

    @classmethod
    def err(cls, code: int = 1, message: str = "error"):
        return cls(code=code, message=message, data=None)


# ============ Auth ============

PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")


def _validate_phone(v: str) -> str:
    if not PHONE_PATTERN.match(v):
        raise ValueError("手机号格式不正确，请输入11位手机号")
    return v


class RegisterReq(BaseModel):
    phone: str = Field(..., max_length=20)
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(..., pattern="^(parent|teacher)$")
    real_name: Optional[str] = Field("", max_length=50)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_phone(v)


class LoginReq(BaseModel):
    phone: str
    password: str


class LoginResp(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfoResp


class UserInfoResp(BaseModel):
    id: int
    role: str
    phone: str
    nickname: str = ""
    avatar: str = ""
    status: str


class ProfileUpdateReq(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None


class PasswordUpdateReq(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


# ============ Teacher ============

class TeacherListQuery(BaseModel):
    subject: Optional[str] = None
    city: Optional[str] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    min_rating: Optional[float] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class TeacherProfileCreate(BaseModel):
    real_name: str = Field(..., max_length=50)
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    education: str = Field("", max_length=100)
    title: str = Field("", max_length=100)
    subject_tags: list[str] = Field(..., min_length=1)
    experience_years: int = Field(0, ge=0)
    hourly_rate: float = Field(0, ge=0)
    city: str = Field("", max_length=50)
    district: str = Field("", max_length=50)
    qualification_url: str = ""
    bio: str = ""


# ============ Student ============

class StudentCreate(BaseModel):
    real_name: str = Field(..., max_length=50)
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    grade: str = Field("", max_length=20)
    school: str = Field("", max_length=100)
    subjects: Optional[list[str]] = None


class StudentUpdate(BaseModel):
    real_name: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    grade: Optional[str] = Field(None, max_length=20)
    school: Optional[str] = Field(None, max_length=100)
    subjects: Optional[list[str]] = None


# ============ Binding ============

class BindingCreate(BaseModel):
    teacher_id: int
    student_id: int
    reply_message: Optional[str] = None


class BindingReply(BaseModel):
    action: str = Field(..., pattern="^(accept|reject)$")
    reply_message: Optional[str] = None


# ============ Assignment ============

class AssignmentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    content_images: Optional[list[str]] = None
    due_at: datetime
    max_score: float = Field(100, ge=0)
    student_ids: list[int] = Field(..., min_length=1)


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    content_images: Optional[list[str]] = None
    due_at: Optional[datetime] = None
    max_score: Optional[float] = Field(None, ge=0)


class GradeRequest(BaseModel):
    score: float
    comment: Optional[str] = None


# ============ Announcement ============

class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    publish_from: datetime
    publish_to: Optional[datetime] = None
    is_active: int = Field(1, ge=0, le=1)


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    publish_from: Optional[datetime] = None
    publish_to: Optional[datetime] = None
    is_active: Optional[int] = None


# ============ IM ============

class MessageResp(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    msg_type: str
    content: str
    is_read: int
    created_at: datetime
    sender_name: str = ""
    sender_avatar: str = ""


class ConversationResp(BaseModel):
    id: int
    conversation_key: str
    participant_1_id: int
    participant_2_id: int
    last_message: Optional[MessageResp] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime
