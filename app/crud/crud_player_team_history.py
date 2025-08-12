from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_player_team_history(
    session: Session, history_id: UUID
) -> models.PlayerTeamHistory | None:
    statement = (
        select(models.PlayerTeamHistory)
        .where(models.PlayerTeamHistory.id == history_id)
        .options(
            selectinload(models.PlayerTeamHistory.player),  # type: ignore[arg-type]
            selectinload(models.PlayerTeamHistory.team),  # type: ignore[arg-type]
            selectinload(models.PlayerTeamHistory.season),  # type: ignore[arg-type]
        )
    )
    return session.exec(statement).first()


def get_player_team_histories(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    player_id: UUID | None = None,
    team_id: UUID | None = None,
    season_id: UUID | None = None,
) -> Sequence[models.PlayerTeamHistory]:
    statement = select(models.PlayerTeamHistory)

    if player_id:
        statement = statement.where(models.PlayerTeamHistory.player_id == player_id)
    if team_id:
        statement = statement.where(models.PlayerTeamHistory.team_id == team_id)
    if season_id:
        statement = statement.where(models.PlayerTeamHistory.season_id == season_id)

    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def create_player_team_history(
    session: Session, history: models.PlayerTeamHistoryCreate
) -> models.PlayerTeamHistory:
    db_history = models.PlayerTeamHistory.model_validate(history)
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history


def update_player_team_history(
    session: Session,
    db_history: models.PlayerTeamHistory,
    history_update: models.PlayerTeamHistoryUpdate,
) -> models.PlayerTeamHistory:
    update_data = history_update.model_dump(exclude_unset=True)
    db_history.sqlmodel_update(update_data)

    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history
