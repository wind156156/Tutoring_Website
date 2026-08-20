from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.core.config import settings
from app.core.database import get_db
from app.schemas import BaseResponse

router = APIRouter(prefix="/files", tags=["文件上传"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _safe_filename(filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    return f"{uuid.uuid4().hex}{ext}"


@router.post("/upload", response_model=BaseResponse)
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Upload a file and return its URL."""
    allowed_exts = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip', '.rar'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")

    safe_name = _safe_filename(file.filename)
    dest_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest_path, "wb") as f:
        f.write(content)

    url = f"/api/v1/files/served/{safe_name}"
    return BaseResponse.ok(data={"url": url, "name": file.filename, "size": len(content)})


@router.get("/served/{filename}")
async def serve_file(filename: str):
    """Serve uploaded files."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    from fastapi.responses import FileResponse
    return FileResponse(file_path, filename=filename)
