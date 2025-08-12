from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_season(session: Session, season_id: UUID) -> models.Season | None:
    return session.get(models.Season, season_id)


def get_seasons(
    session: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.Season]:
    statement = select(models.Season).offset(skip).limit(limit)
    results = session.exec(statement)
    return results.all()


def create_season(session: Session, season: models.SeasonCreate) -> models.Season:
    db_season = models.Season.model_validate(season)
    session.add(db_season)
    session.commit()
    session.refresh(db_season)
    return db_season


def update_season(
    session: Session, db_season: models.Season, season_update: models.SeasonUpdate
) -> models.Season:
    update_data = season_update.model_dump(exclude_unset=True)
    db_season.sqlmodel_update(update_data)

    session.add(db_season)
    session.commit()
    session.refresh(db_season)
    return db_season


def delete_season(session: Session, db_season: models.Season) -> None:
    session.delete(db_season)
    session.commit()
    return