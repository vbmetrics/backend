from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Team, TeamCreate, TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    def get(self, db: Session, id: UUID) -> Team | None:
        """
        Overwrites get method to add eager loading
        for 'country' and 'home_arena' relationship.
        """
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.country),  # type: ignore[arg-type]
                selectinload(self.model.home_arena),  # type: ignore[arg-type]
            )
        )
        return db.exec(statement).first()

    def get_by_name(self, db: Session, name: str) -> Team | None:
        statement = select(self.model).where(self.model.name == name)
        return db.exec(statement).first()


team = CRUDTeam(Team)
