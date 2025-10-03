from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import or_
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Team, TeamType
from app.schemas import TeamCreateDTO, TeamUpdateDTO


class CRUDTeam(CRUDBase[Team, TeamCreateDTO, TeamUpdateDTO]):
    def get(self, db: Session, id: UUID) -> Team | None:
        """
        Overwrites get method to add eager loading
        for 'country' and 'home_arena' relationship.
        """
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_by_name(self, db: Session, name: str) -> Team | None:
        statement = select(self.model).where(self.model.name == name)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        team_type: TeamType | None = None,
        country_code: str | None = None,
        home_arena_id: UUID | None = None,
        search: str | None = None,  # name/email/website
    ) -> Sequence[Team]:
        statement = select(self.model)

        # mypy-safe columns
        type_col: Any = self.model.team_type
        country_col: Any = self.model.country_code
        arena_col: Any = self.model.home_arena_id
        name_col: Any = self.model.name
        email_col: Any = self.model.email
        www_col: Any = self.model.website_url
        created_col: Any = self.model.created_at

        if team_type:
            statement = statement.where(type_col == team_type)
        if country_code:
            statement = statement.where(country_col == country_code)
        if home_arena_id:
            statement = statement.where(arena_col == home_arena_id)
        if search:
            ilike = f"%{search}%"
            statement = statement.where(
                or_(
                    name_col.ilike(ilike),  # type: ignore[attr-defined]
                    email_col.ilike(ilike),  # type: ignore[attr-defined]
                    www_col.ilike(ilike),  # type: ignore[attr-defined]
                )
            )

        statement = statement.order_by(name_col, created_col).offset(skip).limit(limit)
        return cast(Sequence[Team], db.exec(statement).all())


team = CRUDTeam(Team)
