from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .. import models


def get_staff_member(
    session: Session, staff_member_id: UUID
) -> models.StaffMember | None:
    statement = (
        select(models.StaffMember)
        .where(models.StaffMember.id == staff_member_id)
        .options(selectinload(models.StaffMember.nationality))  # type: ignore[arg-type]
    )
    return session.exec(statement).first()


def get_staff_members(
    session: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.StaffMember]:
    statement = select(models.StaffMember).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_staff_member(
    session: Session, staff_member: models.StaffMemberCreate
) -> models.StaffMember:
    db_staff_member = models.StaffMember.model_validate(staff_member)
    session.add(db_staff_member)
    session.commit()
    session.refresh(db_staff_member)
    return db_staff_member


def update_staff_member(
    session: Session,
    db_staff_member: models.StaffMember,
    staff_member_update: models.StaffMemberUpdate,
) -> models.StaffMember:
    update_data = staff_member_update.model_dump(exclude_unset=True)
    db_staff_member.sqlmodel_update(update_data)

    session.add(db_staff_member)
    session.commit()
    session.refresh(db_staff_member)
    return db_staff_member


def delete_staff_member(session: Session, db_staff_member: models.StaffMember) -> None:
    session.delete(db_staff_member)
    session.commit()
    return
