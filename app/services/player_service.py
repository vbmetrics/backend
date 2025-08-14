from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_player import CRUDPlayer


class PlayerService:
    def __init__(self, player_crud: CRUDPlayer):
        self.player_crud = player_crud

    def get_by_id(self, db: Session, player_id: UUID) -> models.Player:
        db_player = self.player_crud.get(db=db, id=player_id)
        if not db_player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
            )
        return db_player

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[models.Player]:
        return self.player_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, player_in: models.PlayerCreate) -> models.Player:
        return self.player_crud.create(db=db, obj_in=player_in)

    def update(
        self, db: Session, player_id: UUID, player_in: models.PlayerUpdate
    ) -> models.Player:
        db_player = self.get_by_id(db=db, player_id=player_id)
        return self.player_crud.update(db=db, db_obj=db_player, obj_in=player_in)

    def delete(self, db: Session, player_id: UUID) -> models.Player:
        db_player = self.get_by_id(db=db, player_id=player_id)
        return self.player_crud.remove(db=db, db_obj=db_player)


player_service = PlayerService(crud.player)
