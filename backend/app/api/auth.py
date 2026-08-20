from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.schemas import (
    BaseResponse, RegisterReq, LoginReq, LoginResp, UserInfoResp,
    ProfileUpdateReq, PasswordUpdateReq
)
from app.models import User, Teacher, Parent

router = APIRouter(prefix="/auth", tags=["认证"])


def _user_to_resp(user: User) -> UserInfoResp:
    return UserInfoResp(
        id=user.id,
        role=user.role,
        phone=user.phone,
        nickname=user.nickname,
        avatar=user.avatar,
        status=user.status,
    )


@router.post("/register", response_model=BaseResponse)
def register(req: RegisterReq, db: Session = Depends(get_db)):
    # Check if phone already exists
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    # Set nickname based on role: parent uses real_name, others use phone prefix
    nickname = req.real_name if req.role == "parent" and req.real_name else req.phone[:8]

    user = User(
        phone=req.phone,
        password_hash=hash_password(req.password),
        role=req.role,
        nickname=nickname,
        status="active",
    )
    db.add(user)
    db.flush()

    # Auto-create role-specific profile
    if req.role == "teacher":
        db.add(Teacher(user_id=user.id, real_name=req.phone[:8]))
    elif req.role == "parent":
        db.add(Parent(user_id=user.id, real_name=req.real_name or req.phone[:8]))

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})
    return BaseResponse.ok(data=LoginResp(
        access_token=token,
        user=_user_to_resp(user),
    ).model_dump())


@router.post("/login/password", response_model=BaseResponse)
def login_password(req: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    if user.status == "frozen":
        raise HTTPException(status_code=403, detail="账号已被冻结")

    token = create_access_token({"sub": user.id, "role": user.role})
    return BaseResponse.ok(data=LoginResp(
        access_token=token,
        user=_user_to_resp(user),
    ).model_dump())


@router.get("/me", response_model=BaseResponse)
def get_me(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.id == user["id"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    return BaseResponse.ok(data=_user_to_resp(u).model_dump())


@router.put("/profile", response_model=BaseResponse)
def update_profile(
    req: ProfileUpdateReq,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.id == user["id"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    if req.nickname is not None:
        u.nickname = req.nickname
    if req.avatar is not None:
        u.avatar = req.avatar

    db.commit()
    db.refresh(u)
    return BaseResponse.ok(data=_user_to_resp(u).model_dump())


@router.put("/password", response_model=BaseResponse)
def update_password(
    req: PasswordUpdateReq,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    u = db.query(User).filter(User.id == user["id"]).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(req.old_password, u.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")

    u.password_hash = hash_password(req.new_password)
    db.commit()
    return BaseResponse.ok(message="密码修改成功")
