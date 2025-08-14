from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_team import CRUDTeam


class TeamService:
    def __init__(self, team_crud: CRUDTeam):
        self.team_crud = team_crud

    def get_by_id(self, db, team_id: UUID) -> models.Team:
        db_team = self.team_crud.get(db=db, id=team_id)
        if not db_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )
        return db_team

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[models.Team]:
        return self.team_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, team_in: models.TeamCreate) -> models.Team:
        return self.team_crud.create(db=db, obj_in=team_in)

    def update(
        self, db: Session, team_id: UUID, team_in: models.TeamUpdate
    ) -> models.Team:
        db_team = self.get_by_id(db=db, team_id=team_id)
        return self.team_crud.update(db=db, db_obj=db_team, obj_in=team_in)

    def delete(self, db: Session, team_id: UUID) -> models.Team:
        db_team = self.get_by_id(db=db, team_id=team_id)
        return self.team_crud.remove(db=db, db_obj=db_team)


team_service = TeamService(crud.team)
