from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_team(session: Session, team_id: UUID) -> models.Team | None:
    statement = (
        select(models.Team)
        .where(models.Team.id == team_id)
        .options(
            selectinload(models.Team.country),  # type: ignore[arg-type]
            selectinload(models.Team.home_arena),  # type: ignore[arg-type]
        )
    )
    return session.exec(statement).first()


def get_teams(
    session: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.Team]:
    statement = select(models.Team).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_team(session: Session, team: models.TeamCreate) -> models.Team:
    db_team = models.Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


def update_team(
    session: Session, db_team: models.Team, team_update: models.TeamUpdate
) -> models.Team:
    update_data = team_update.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(update_data)

    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


def delete_team(session: Session, db_team: models.Team) -> None:
    session.delete(db_team)
    session.commit()
    return
