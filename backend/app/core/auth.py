from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token

security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """Extract and validate JWT from Authorization header."""
    token = credentials.credentials
    token_data = decode_access_token(token)
    if token_data is None or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attach to request state for use in business logic
    request.state.current_user_id = token_data.user_id
    request.state.current_role = token_data.role
    return {"id": token_data.user_id, "role": token_data.role}


def require_role(*roles: str):
    """Dependency factory: require one of the given roles."""
    async def _checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return _checker


def get_current_user_id(request: Request) -> int:
    """Quick accessor for current user ID from request state."""
    return request.state.current_user_id
