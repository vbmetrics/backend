from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_set import CRUDSet


class SetService:
    def __init__(self, set_crud: CRUDSet):
        self.set_crud = set_crud

    def get_by_id(self, db: Session, set_id: UUID) -> models.Set:
        db_set = self.set_crud.get(db=db, id=set_id)
        if not db_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
            )
        return db_set

    def get_all(
        self,
        db: Session,
        *,
        skip: int,
        limit: int,
        match_id: UUID | None = None,
        winner_team_id: UUID | None = None,
    ) -> Sequence[models.Set]:
        return self.set_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            match_id=match_id,
            winner_team_id=winner_team_id,
        )

    def create(self, db: Session, set_in: models.SetCreate) -> models.Set:
        existing_set = self.set_crud.get_by_match_id_and_set_number(
            db, match_id=set_in.match_id, set_number=set_in.set_number
        )
        if existing_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Set number {set_in.set_number} already exists for this match.",
            )
        return self.set_crud.create(db=db, obj_in=set_in)

    def update(self, db: Session, set_id: UUID, set_in: models.SetUpdate) -> models.Set:
        db_set = self.get_by_id(db=db, set_id=set_id)

        if set_in.winner_team_id and set_in.winner_team_id not in [
            db_set.match.home_team_id,
            db_set.match.away_team_id,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Winner must be one of the participating teams.",
            )

        return self.set_crud.update(db=db, db_obj=db_set, obj_in=set_in)

    def delete(self, db: Session, set_id: UUID) -> models.Set:
        db_set = self.get_by_id(db=db, set_id=set_id)

        return self.set_crud.remove(db=db, db_obj=db_set)


set_service = SetService(crud.set)
