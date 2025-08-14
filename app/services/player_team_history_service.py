from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_player_team_history import CRUDPlayerTeamHistory


class PlayerTeamHistoryService:
    def __init__(self, player_team_history_crud: CRUDPlayerTeamHistory):
        self.player_team_history_crud = player_team_history_crud

    def get_by_id(self, db: Session, history_id: UUID) -> models.PlayerTeamHistory:
        db_history = self.player_team_history_crud.get(db, id=history_id)
        if not db_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player-Team History not found",
            )
        return db_history

    def get_all(
        self, db: Session, skip: int, limit: int
    ) -> Sequence[models.PlayerTeamHistory]:
        return self.player_team_history_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(
        self, db: Session, history_in: models.PlayerTeamHistoryCreate
    ) -> models.PlayerTeamHistory:
        return self.player_team_history_crud.create(db=db, obj_in=history_in)

    def update(
        self, db: Session, history_id: UUID, history_in: models.PlayerTeamHistoryUpdate
    ) -> models.PlayerTeamHistory:
        db_history = self.get_by_id(db=db, history_id=history_id)
        return self.player_team_history_crud.update(
            db=db, db_obj=db_history, obj_in=history_in
        )

    def delete(self, db: Session, history_id: UUID) -> models.PlayerTeamHistory:
        db_history = self.get_by_id(db=db, history_id=history_id)
        return self.player_team_history_crud.remove(db=db, db_obj=db_history)


player_team_history_service = PlayerTeamHistoryService(crud.player_team_history)
