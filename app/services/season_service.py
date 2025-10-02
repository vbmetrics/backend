from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_season import CRUDSeason
from app.models.season import Season, SeasonType
from app.schemas import SeasonCreateDTO, SeasonUpdateDTO
from app.services.errors import BadRequestError, ConflictError, NotFoundError


class SeasonService:
    def __init__(self, season_crud: CRUDSeason):
        self.season_crud = season_crud

    # ---------- helpers ----------

    @staticmethod
    def _validate_dates(start_date: date, end_date: date) -> None:
        if end_date < start_date:
            raise BadRequestError(
                "end_date cannot be earlier than start_date", code="INVALID_DATE_RANGE"
            )

    # ---------- CRUD ----------

    def get_by_id(self, db: Session, season_id: UUID) -> Season:
        db_season = self.season_crud.get(db=db, id=season_id)
        if not db_season:
            raise NotFoundError(
                "Season not found",
                code="SEASON_NOT_FOUND",
                details={"season_id": str(season_id)},
            )
        return db_season

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        season_type: SeasonType | None = None,
        active_on: date | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> Sequence[Season]:
        return self.season_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            season_type=season_type,
            active_on=active_on,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )

    def create(self, db: Session, season_in: SeasonCreateDTO) -> Season:
        self._validate_dates(season_in.start_date, season_in.end_date)
        if self.season_crud.get_by_name(db, season_in.name):
            raise ConflictError(
                "Season name already exists",
                code="SEASON_NAME_EXISTS",
                details={"name": season_in.name},
            )
        return self.season_crud.create(db=db, obj_in=season_in)

    def update(
        self, db: Session, season_id: UUID, season_in: SeasonUpdateDTO
    ) -> Season:
        obj = self.get_by_id(db=db, season_id=season_id)

        data = season_in.model_dump(exclude_unset=True)

        if "start_date" in data or "end_date" in data:
            start = data.get("start_date", obj.start_date)
            end = data.get("end_date", obj.end_date)
            self._validate_dates(start, end)

        if "name" in data and data["name"] != obj.name:
            if self.season_crud.get_by_name(db, data["name"]):
                raise ConflictError(
                    "Season name already exists",
                    code="SEASON_NAME_EXISTS",
                    details={"name": data["name"]},
                )

        return self.season_crud.update(db=db, db_obj=obj, obj_in=season_in)

    def delete(self, db: Session, season_id: UUID) -> Season:
        db_season = self.get_by_id(db=db, season_id=season_id)
        return self.season_crud.remove(db=db, db_obj=db_season)
