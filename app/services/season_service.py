from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_season import CRUDSeason


class SeasonService:
    def __init__(self, season_crud: CRUDSeason):
        self.season_crud = season_crud

    def get_by_id(self, db: Session, season_id: UUID) -> models.Season:
        db_season = self.season_crud.get(db=db, id=season_id)
        if not db_season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Season not found"
            )
        return db_season

    def get_all(self, db: Session, skip: int, limit: int) -> Sequence[models.Season]:
        return self.season_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, season_in: models.SeasonCreate) -> models.Season:
        return self.season_crud.create(db=db, obj_in=season_in)

    def update(
        self, db: Session, season_id: UUID, season_in: models.SeasonUpdate
    ) -> models.Season:
        db_season = self.get_by_id(db=db, season_id=season_id)
        return self.season_crud.update(db=db, db_obj=db_season, obj_in=season_in)

    def delete(self, db: Session, season_id: UUID) -> models.Season:
        db_season = self.get_by_id(db=db, season_id=season_id)
        return self.season_crud.remove(db=db, db_obj=db_season)


season_service = SeasonService(crud.season)
