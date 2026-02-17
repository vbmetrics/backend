from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_player_team_history import CRUDPlayerTeamHistory
from app.models.player_team_history import PlayerTeamHistory
from app.schemas import (
    PlayerTeamHistoryCreateDTO,
    PlayerTeamHistoryUpdateDTO,
)
from app.services.errors import BadRequestError, ConflictError, NotFoundError


class PlayerTeamHistoryService:
    def __init__(self, player_team_history_crud: CRUDPlayerTeamHistory):
        self.pth_crud = player_team_history_crud

    # ---------- helpers ----------

    @staticmethod
    def _validate_dates(start_date: date, end_date: date | None) -> None:
        if end_date and end_date < start_date:
            raise BadRequestError(
                "end_date cannot be earlier than start_date", code="INVALID_DATE_RANGE"
            )

    # ---------- CRUD ----------

    def get_by_id(self, db: Session, pth_id: UUID) -> PlayerTeamHistory:
        db_history = self.pth_crud.get(db=db, id=pth_id)
        if not db_history:
            raise NotFoundError(
                "Player team history not found",
                code="PTH_NOT_FOUND",
                details={"id": str(pth_id)},
            )
        return db_history

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        player_id: UUID | None = None,
        team_id: UUID | None = None,
        season_id: list[UUID] | None = None,
        active_on: date | None = None,
    ) -> Sequence[PlayerTeamHistory]:
        return self.pth_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            player_id=player_id,
            team_id=team_id,
            season_id=season_id,
            active_on=active_on,
        )

    def create(
        self, db: Session, history_in: PlayerTeamHistoryCreateDTO
    ) -> PlayerTeamHistory:
        self._validate_dates(history_in.start_date, history_in.end_date)
        # Disallow overlapping entries within the same (player, season)
        if self.pth_crud.any_overlapping(
            db,
            player_id=history_in.player_id,
            season_id=history_in.season_id,
            start_date=history_in.start_date,
            end_date=history_in.end_date,
        ):
            raise ConflictError(
                "Overlapping player-team history entry for this season",
                code="PTH_OVERLAP",
                details={
                    "player_id": str(history_in.player_id),
                    "season_id": str(history_in.season_id),
                    "start_date": str(history_in.start_date),
                    "end_date": str(history_in.end_date),
                },
            )
        return self.pth_crud.create(db=db, obj_in=history_in)

    def update(
        self, db: Session, pth_id: UUID, history_in: PlayerTeamHistoryUpdateDTO
    ) -> PlayerTeamHistory:
        db_history = self.get_by_id(db=db, pth_id=pth_id)

        data = history_in.model_dump(exclude_unset=True)
        start = data.get("start_date", db_history.start_date)
        end = data.get("end_date", db_history.end_date)
        player_id = data.get("player_id", db_history.player_id)
        season_id = data.get("season_id", db_history.season_id)

        self._validate_dates(start, end)
        if self.pth_crud.any_overlapping(
            db,
            player_id=player_id,
            season_id=season_id,
            start_date=start,
            end_date=end,
            exclude_id=db_history.id,
        ):
            raise ConflictError(
                "Overlapping player-team history entry for this season",
                code="PTH_OVERLAP",
                details={
                    "player_id": str(player_id),
                    "season_id": str(season_id),
                    "start_date": str(start),
                    "end_date": str(end),
                },
            )

        return self.pth_crud.update(db=db, db_obj=db_history, obj_in=history_in)

    def delete(self, db: Session, pth_id: UUID) -> PlayerTeamHistory:
        db_history = self.get_by_id(db=db, pth_id=pth_id)
        return self.pth_crud.remove(db=db, db_obj=db_history)
