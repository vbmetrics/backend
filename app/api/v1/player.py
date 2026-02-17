from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.player import PlayerPosition
from app.models.user import UserRole
from app.schemas import PlayerCreateDTO, PlayerReadDTO, PlayerUpdateDTO
from app.services.player_service import PlayerService

router = APIRouter(prefix="/player", tags=["Player"])


@router.post(
    "/",
    response_model=PlayerReadDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def create_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_in: PlayerCreateDTO,
    service: PlayerService = Depends(deps.get_player_service),
):
    return service.create(db=db, player_in=player_in)


@router.get(
    "/",
    response_model=list[PlayerReadDTO],
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_players_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    nationality_code: str | None = None,
    playing_position: PlayerPosition | None = None,
    search: str | None = None,
    service: PlayerService = Depends(deps.get_player_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        nationality_code=nationality_code,
        playing_position=playing_position,
        search=search,
    )


@router.get(
    "/{player_id}",
    response_model=PlayerReadDTO,
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_id: UUID,
    service: PlayerService = Depends(deps.get_player_service),
):
    return service.get_by_id(db=db, player_id=player_id)


@router.patch(
    "/{player_id}",
    response_model=PlayerReadDTO,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def update_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_id: UUID,
    player_in: PlayerUpdateDTO,
    service: PlayerService = Depends(deps.get_player_service),
):
    return service.update(db=db, player_id=player_id, player_in=player_in)


@router.delete(
    "/{player_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def delete_player_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    player_id: UUID,
    service: PlayerService = Depends(deps.get_player_service),
):
    service.delete(db=db, player_id=player_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
