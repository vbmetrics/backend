from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_team import CRUDTeam
from app.models.team import Team, TeamType
from app.schemas import TeamCreateDTO, TeamUpdateDTO
from app.services.errors import BadRequestError, ConflictError, NotFoundError


class TeamService:
    def __init__(self, team_crud: CRUDTeam):
        self.team_crud = team_crud

    def get_by_id(self, db: Session, team_id: UUID) -> Team:
        db_team = self.team_crud.get(db=db, id=team_id)
        if not db_team:
            raise NotFoundError(
                "Team not found",
                code="TEAM_NOT_FOUND",
                details={"team_id": str(team_id)},
            )
        return db_team

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        team_type: TeamType | None = None,
        country_code: str | None = None,
        home_arena_id: UUID | None = None,
        search: str | None = None,
    ) -> Sequence[Team]:
        return self.team_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            team_type=team_type,
            country_code=country_code,
            home_arena_id=home_arena_id,
            search=search,
        )

    def create(self, db: Session, team_in: TeamCreateDTO) -> Team:
        if len(team_in.country_code) != 2:
            raise BadRequestError(
                "country_code must be 2 letters", code="INVALID_COUNTRY_CODE"
            )
        # unique name check
        if self.team_crud.get_by_name(db, team_in.name):
            raise ConflictError(
                "Team name already exists",
                code="TEAM_NAME_EXISTS",
                details={"name": team_in.name},
            )
        return self.team_crud.create(db=db, obj_in=team_in)

    def update(self, db: Session, team_id: UUID, team_in: TeamUpdateDTO) -> Team:
        obj = self.get_by_id(db=db, team_id=team_id)

        data = team_in.model_dump(exclude_unset=True)
        if (
            "country_code" in data
            and data["country_code"]
            and len(data["country_code"]) != 2
        ):
            raise BadRequestError(
                "country_code must be 2 letters", code="INVALID_COUNTRY_CODE"
            )

        if "name" in data and data["name"] != obj.name:
            if self.team_crud.get_by_name(db, data["name"]):
                raise ConflictError(
                    "Team name already exists",
                    code="TEAM_NAME_EXISTS",
                    details={"name": data["name"]},
                )

        return self.team_crud.update(db=db, db_obj=obj, obj_in=team_in)

    def delete(self, db: Session, team_id: UUID) -> Team:
        db_team = self.get_by_id(db=db, team_id=team_id)
        return self.team_crud.remove(db=db, db_obj=db_team)
