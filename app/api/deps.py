from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from app import models
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.user_service import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]
Token = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(db: DBSession, token: Token) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = models.token.TokenData(email=payload.get("sub"))
    except (JWTError, AttributeError):
        credentials_exception

    if token_data.email is None:
        raise credentials_exception

    user = user_service.get_by_email(db=db, email=token_data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: models.user.UserRole):
    def check_user_role(current_user: CurrentUser) -> None:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have right privileges",
            )

    return check_user_role


CurrentUser = Annotated[models.User, Depends(get_current_active_user)]
