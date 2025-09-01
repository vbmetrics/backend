from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_rally import CRUDRally


class RallyService:
    def __init__(self, rally_crud: CRUDRally):
        self.rally_crud = rally_crud

    def get_by_id(self, db: Session, rally_id: UUID) -> models.Rally:
        db_rally = self.rally_crud.get(db=db, id=rally_id)
        if not db_rally:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rally not found"
            )
        return db_rally

    def get_all(
        self,
        db: Session,
        *,
        skip: int,
        limit: int,
        set_id: UUID | None = None,
        serve_team_id: UUID | None = None,
        score_team_id: UUID | None = None,
    ) -> Sequence[models.Rally]:
        return self.rally_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            set_id=set_id,
            serve_team_id=serve_team_id,
            score_team_id=score_team_id,
        )

    def create(self, db: Session, rally_in: models.RallyCreate) -> models.Rally:
        # Rule 1: context (set) integrity
        parent_set = crud.set.get_with_match(db, id=rally_in.set_id)
        if not parent_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Set with id {rally_in.set_id} not found",
            )

        # Rule 2: teams integrity
        match_teams = {parent_set.match.home_team_id, parent_set.match.away_team_id}
        if rally_in.serve_team_id not in match_teams:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Serving team is not a participant in this match.",
            )
        if rally_in.score_team_id not in match_teams:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scoring team is not a participant in this match.",
            )

        # Rule 3: unique rally number in set
        existing_rally = self.rally_crud.get_by_set_id_and_rally_number(
            db,
            set_id=rally_in.set_id,
            rally_number=rally_in.rally_number_in_set,
        )
        if existing_rally:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rally number {rally_in.rally_number_in_set}",
            )

        return self.rally_crud.create(db=db, obj_in=rally_in)

    def update(
        self, db: Session, rally_id: UUID, rally_in: models.RallyUpdate
    ) -> models.Rally:
        db_rally = self.get_by_id(db=db, rally_id=rally_id)

        # TODO: rules and business logic

        return self.rally_crud.update(db=db, db_obj=db_rally, obj_in=rally_in)

    def delete(self, db: Session, rally_id: UUID) -> models.Rally:
        db_rally = self.get_by_id(db=db, rally_id=rally_id)

        # TODO: business logic for delete, cascade score recalculation

        return self.rally_crud.remove(db=db, db_obj=db_rally)


rally_service = RallyService(crud.rally)
