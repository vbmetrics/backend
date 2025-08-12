from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_player(session: Session, player_id: UUID) -> models.Player | None:
    statement = (
        select(models.Player)
        .where(models.Player.id == player_id)
        .options(selectinload(models.Player.nationality))  # type: ignore[arg-type]
    )
    return session.exec(statement).first()


def get_players(
    session: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.Player]:
    statement = select(models.Player).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_player(session: Session, player: models.PlayerCreate) -> models.Player:
    db_player = models.Player.model_validate(player)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player


def update_player(
    session: Session, db_player: models.Player, player_update: models.PlayerUpdate
) -> models.Player:
    update_data = player_update.model_dump(exclude_unset=True)
    db_player.sqlmodel_update(update_data)

    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player


def delete_player(session: Session, db_player: models.Player) -> None:
    session.delete(db_player)
    session.commit()
    return