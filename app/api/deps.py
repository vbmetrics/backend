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
from app.crud.crud_player_team_history import player_team_history as pth_crud
from app.crud.crud_rally import rally as rally_crud
from app.crud.crud_season import season as season_crud
from app.crud.crud_set import vb_set as set_crud
from app.crud.crud_special_event import special_event as special_event_crud
from app.crud.crud_staff_member import staff_member as staff_member_crud
from app.crud.crud_staff_team_history import staff_team_history as sth_crud
from app.crud.crud_team import team as team_crud
from app.db.session import SessionLocal
from app.services.action_service import ActionService
from app.services.arena_service import ArenaService
from app.services.country_service import CountryService
from app.services.match_service import MatchService
from app.services.player_service import PlayerService
from app.services.player_team_history_service import PlayerTeamHistoryService
from app.services.rally_service import RallyService
from app.services.season_service import SeasonService
from app.services.set_service import SetService
from app.services.special_event_service import SpecialEventService
from app.services.staff_member_service import StaffMemberService
from app.services.staff_team_history_service import StaffTeamHistoryService
from app.services.team_service import TeamService
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


def get_player_team_history_service() -> PlayerTeamHistoryService:
    return PlayerTeamHistoryService(player_team_history_crud=pth_crud)


def get_rally_service() -> RallyService:
    return RallyService(
        rally_crud_dep=rally_crud, action_crud_dep=action_crud, parser=CodeParser()
    )


def get_season_service() -> SeasonService:
    return SeasonService(season_crud=season_crud)


def get_set_service() -> SetService:
    return SetService(set_crud_dep=set_crud, match_crud_dep=match_crud)


def get_staff_member_service() -> StaffMemberService:
    return StaffMemberService(staff_member_crud=staff_member_crud)


def get_staff_team_history_service() -> StaffTeamHistoryService:
    return StaffTeamHistoryService(staff_team_history_crud=sth_crud)


def get_team_service() -> TeamService:
    return TeamService(team_crud=team_crud)


def get_special_event_service() -> SpecialEventService:
    return SpecialEventService(special_event_crud=special_event_crud)


CurrentUser = Annotated[models.User, Depends(get_current_active_user)]
