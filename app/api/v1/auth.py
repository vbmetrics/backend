from fastapi import APIRouter, Depends, Request, Response, status
from sqlmodel import Session

from app.api import deps
from app.schemas.auth import LoginDTO, MeReadDTO, RefreshDTO, TokenPairDTO
from app.schemas.user import UserCreateDTO, UserReadDTO
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()
user_service = UserService()


@router.post(
    "/register", response_model=UserReadDTO, status_code=status.HTTP_201_CREATED
)
def register(*, db: Session = Depends(deps.get_db), body: UserCreateDTO):
    return user_service.create(db=db, body=body)


@router.post("/login", response_model=TokenPairDTO)
def login(*, request: Request, db: Session = Depends(deps.get_db), body: LoginDTO):
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    access, refresh, expires_in = auth_service.login(
        db, email=body.email, password=body.password, user_agent=ua, ip=ip
    )
    return TokenPairDTO(
        access_token=access, refresh_token=refresh, expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenPairDTO)
def refresh(*, db: Session = Depends(deps.get_db), body: RefreshDTO):
    access, refresh, expires_in = auth_service.refresh(
        db, refresh_token=body.refresh_token
    )
    return TokenPairDTO(
        access_token=access, refresh_token=refresh, expires_in=expires_in
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def logout(*, db: Session = Depends(deps.get_db), body: RefreshDTO):
    auth_service.logout(db=db, refresh_token=body.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=MeReadDTO)
def me(current_user=Depends(deps.get_current_user)):
    return MeReadDTO(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
    )
