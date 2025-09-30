from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_player import CRUDPlayer
from app.models import Player, PlayerPosition
from app.schemas import PlayerCreateDTO, PlayerUpdateDTO
from app.services.errors import BadRequestError, NotFoundError


class PlayerService:
    def __init__(self, player_crud: CRUDPlayer):
        self.player_crud = player_crud

    def get_by_id(self, db: Session, player_id: UUID) -> Player:
        db_player = self.player_crud.get(db=db, id=player_id)
        if not db_player:
            raise NotFoundError(
                "Player not found",
                code="PLAYER_NOT_FOUND",
                details={"player_id": str(player_id)},
            )
        return db_player

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        nationality_code: str | None = None,
        playing_position: PlayerPosition | None = None,
        search: str | None = None,
    ) -> Sequence[Player]:
        return self.player_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            nationality_code=nationality_code,
            playing_position=playing_position,
            search=search,
        )

    def create(self, db: Session, player_in: PlayerCreateDTO) -> Player:
        if len(player_in.nationality_code) != 2:
            raise BadRequestError(
                "nationality_code must be 2 letters", code="INVALID_NATIONALITY_CODE"
            )
        return self.player_crud.create(db=db, obj_in=player_in)

    def update(
        self, db: Session, player_id: UUID, player_in: PlayerUpdateDTO
    ) -> Player:
        db_player = self.get_by_id(db=db, player_id=player_id)
        return self.player_crud.update(db=db, db_obj=db_player, obj_in=player_in)

    def delete(self, db: Session, player_id: UUID) -> Player:
        db_player = self.get_by_id(db=db, player_id=player_id)
        return self.player_crud.remove(db=db, db_obj=db_player)
