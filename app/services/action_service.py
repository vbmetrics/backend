from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app import models
from app.crud.crud_action import CRUDAction
from app.services.errors import BadRequestError, ConflictError, NotFoundError


class ActionService:
    def __init__(self, action_crud: CRUDAction):
        self.action_crud = action_crud

    def get_by_id(self, db: Session, action_id: UUID) -> models.Action:
        db_action = self.action_crud.get(db=db, id=action_id)
        if not db_action:
            raise NotFoundError(
                "Action not found",
                code="ACTION_NOT_FOUND",
                details={"action_id": str(action_id)},
            )
        return db_action

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        rally_id: UUID | None = None,
        player_id: UUID | None = None,
    ) -> Sequence[models.Action]:
        return self.action_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            rally_id=rally_id,
            player_id=player_id,
        )

    def create(self, db: Session, action_in: models.ActionCreate) -> models.Action:
        """
        Prepares a new action with data validation and parsing.
        """
        # TODO: other rules

        if action_in.start_zone is not None and not (1 <= action_in.start_zone <= 9):
            raise BadRequestError(
                "start_zone must be between 1 and 9",
                code="INVALID_START_ZONE",
                details={"start_zone": action_in.start_zone},
            )

        existing = self.action_crud.get_by_rally_id_and_sequence(
            db=db, rally_id=action_in.rally_id, sequence=action_in.sequence_in_rally
        )
        if existing:
            raise ConflictError(
                "Sequence already present in this rally",
                code="SEQUENCE_CONFLICT",
                details={
                    "rally_id": str(action_in.rally_id),
                    "sequence_in_rally": action_in.sequence_in_rally,
                    "conflicting_action_id": str(existing.id),
                },
            )

        return self.action_crud.create(db=db, obj_in=action_in)

    def update(
        self, db: Session, action_id: UUID, action_in: models.ActionUpdate
    ) -> models.Action:
        db_action = self.get_by_id(db=db, action_id=action_id)

        # To update raw code data parse once again and validate (!)
        if action_in.raw_action_code:
            # TODO
            # If parsing fails -> BadRequestError with structured field info
            # parsed = parser.parse(action_in.raw_action_code)
            # else:
            #     raise BadRequestError(
            #       "Invalid raw_action_code", code="INVALID_ACTION_CODE", details={...}
            #     )
            pass

        # Implement logic to recalculate score and match (?)

        return self.action_crud.update(db=db, db_obj=db_action, obj_in=action_in)

    def delete(self, db: Session, action_id: UUID) -> models.Action:
        db_action = self.get_by_id(db=db, action_id=action_id)

        return self.action_crud.remove(db=db, db_obj=db_action)
