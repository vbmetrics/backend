from collections.abc import Sequence
from typing import Any, cast

from sqlalchemy import or_
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.country import Country
from app.schemas import CountryCreateDTO, CountryUpdateDTO


class CRUDCountry(CRUDBase[Country, CountryCreateDTO, CountryUpdateDTO]):
    def get(self, db: Session, code: str) -> Country | None:
        statement = select(self.model).where(self.model.alpha_2_code == code)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> Sequence[Country]:
        statement = select(self.model)

        if search:
            ilike = f"%{search}%"
            # cast columns to Any so mypy doesn't complain about `str | None`
            name_col: Any = self.model.name
            code_col: Any = self.model.alpha_2_code
            statement = statement.where(
                or_(name_col.ilike(ilike), code_col.ilike(ilike))
            )

        statement = statement.order_by(self.model.name).offset(skip).limit(limit)
        return cast(Sequence[Country], db.exec(statement).all())


country = CRUDCountry(Country)
