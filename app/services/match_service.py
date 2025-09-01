from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_match import CRUDMatch


class MatchService:
    def __init__(self, match_crud: CRUDMatch):
        self.match_crud = match_crud

    def get_by_id(self, db: Session, match_id: UUID) -> models.Match:
        db_match = self.match_crud.get(db=db, id=match_id)
        if not db_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
            )
        return db_match

    def get_all(
        self,
        db: Session,
        *,
        skip: int,
        limit: int,
        season_id: UUID | None = None,
        team_id: UUID | None = None,
        winner_team_id: UUID | None = None,
    ) -> Sequence[models.Match]:
        return self.match_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            season_id=season_id,
            team_id=team_id,
            winner_team_id=winner_team_id,
        )

    def create(self, db: Session, match_in: models.MatchCreate) -> models.Match:
        if match_in.home_team_id == match_in.away_team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Home team and away team cannot be the same.",
            )

        # TODO: more rules, e.g. the same season (?)

        return self.match_crud.create(db=db, obj_in=match_in)

    def update(
        self, db: Session, match_id: UUID, match_in: models.MatchUpdate
    ) -> models.Match:
        db_match = self.get_by_id(db=db, match_id=match_id)

        if match_in.winner_team_id and match_in.winner_team_id not in [
            db_match.home_team_id,
            db_match.away_team_id,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Winner must be one of the participating teams.",
            )

        return self.match_crud.update(db=db, db_obj=db_match, obj_in=match_in)

    def delete(self, db: Session, match_id: UUID) -> models.Match:
        db_match = self.get_by_id(db=db, match_id=match_id)

        return self.match_crud.remove(db=db, db_obj=db_match)


match_service = MatchService(crud.match)
