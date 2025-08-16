from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app import models
from app.api.deps import CurrentUser, DBSession
from app.core import security
from app.services.user_service import user_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication & Users"],
)


@router.post("/register", response_model=models.UserRead)
def register_user(
    *,
    db: DBSession,
    user_in: models.UserCreate,
):
    user = user_service.create(db=db, user_in=user_in)
    return user


@router.post("/token", response_model=models.Token)
def login_for_access_token(
    response: Response,
    db: DBSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = user_service.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user/me", response_model=models.UserRead)
def read_current_user(current_user: CurrentUser):
    return current_user
