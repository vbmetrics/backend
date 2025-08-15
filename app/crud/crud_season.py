from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models import Season, SeasonCreate, SeasonUpdate


class CRUDSeason(CRUDBase[Season, SeasonCreate, SeasonUpdate]):
    def get_by_name(self, db: Session, name: str) -> Season | None:
        """
        Get an arena by its name.
        """
        statement = select(self.model).where(self.model.name == name)
        return db.exec(statement).first()


season = CRUDSeason(Season)
