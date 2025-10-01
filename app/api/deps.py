from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from app import models
from app.core.config import settings
from app.crud.crud_action import action as action_crud
from app.crud.crud_arena import arena as arena_crud
from app.crud.crud_country import country as country_crud
from app.crud.crud_match import match as match_crud
from app.crud.crud_player import player as player_crud
from app.db.session import SessionLocal
from app.services.action_service import ActionService
from app.services.arena_service import ArenaService
from app.services.country_service import CountryService
from app.services.match_service import MatchService
from app.services.player_service import PlayerService
from app.services.user_service import user_service
from app.utils.code_parser import CodeParser

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


def get_code_parser() -> CodeParser:
    return CodeParser()


def get_action_service(parser: CodeParser = Depends(get_code_parser)) -> ActionService:
    return ActionService(action_crud=action_crud, code_parser=parser)


def get_player_service() -> PlayerService:
    return PlayerService(player_crud=player_crud)


def get_arena_service() -> ArenaService:
    return ArenaService(arena_crud=arena_crud)


def get_country_service() -> CountryService:
    return CountryService(country_crud=country_crud)


def get_match_service() -> MatchService:
    return MatchService(match_crud=match_crud)


CurrentUser = Annotated[models.User, Depends(get_current_active_user)]
