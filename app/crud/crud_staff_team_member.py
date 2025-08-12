from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_staff_team_history(
    session: Session, history_id: UUID
) -> models.StaffTeamHistory | None:
    statement = (
        select(models.StaffTeamHistory)
        .where(models.StaffTeamHistory.id == history_id)
        .options(
            selectinload(models.StaffTeamHistory.staff_member),  # type: ignore[arg-type]
            selectinload(models.StaffTeamHistory.team),  # type: ignore[arg-type]
            selectinload(models.StaffTeamHistory.season),  # type: ignore[arg-type]
        )
    )
    return session.exec(statement).first()


def get_staff_team_histories(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    staff_member_id: UUID | None = None,
    team_id: UUID | None = None,
    season_id: UUID | None = None,
) -> Sequence[models.StaffTeamHistory]:
    statement = select(models.StaffTeamHistory)

    if staff_member_id:
        statement = statement.where(
            models.StaffTeamHistory.staff_member_id == staff_member_id
        )
    if team_id:
        statement = statement.where(models.StaffTeamHistory.team_id == team_id)
    if season_id:
        statement = statement.where(models.StaffTeamHistory.season_id == season_id)

    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def create_staff_team_history(
    session: Session, history: models.StaffTeamHistoryCreate
) -> models.StaffTeamHistory:
    db_history = models.StaffTeamHistory.model_validate(history)
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history
