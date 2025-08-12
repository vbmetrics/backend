from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_country(session: Session, country_code: str) -> models.Country | None:
    return session.get(models.Country, country_code)


def get_countries(
    session: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.Country]:
    statement = select(models.Country).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_country(session: Session, country: models.CountryCreate) -> models.Country:
    db_country = models.Country.model_validate(country)
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


def update_country(
    session: Session, db_country: models.Country, country_update: models.CountryUpdate
) -> models.Country:
    update_data = country_update.model_dump(exclude_unset=True)
    db_country.sqlmodel_update(update_data)

    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


def delete_country(session: Session, db_country: models.Country) -> None:
    session.delete(db_country)
    session.commit()
    return