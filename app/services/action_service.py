from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_action import CRUDAction
from app.models.action import Action
from app.schemas import ActionCreateDTO, ActionUpdateDTO
from app.services.errors import BadRequestError, ConflictError, NotFoundError
from app.utils.code_parser import CodeParser


class ActionService:
    def __init__(self, action_crud: CRUDAction, code_parser: CodeParser):
        self.action_crud = action_crud
        self._parser = code_parser

    def get_by_id(self, db: Session, action_id: UUID) -> Action:
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
    ) -> Sequence[Action]:
        return self.action_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            rally_id=rally_id,
            player_id=player_id,
        )

    def create(self, db: Session, action_in: ActionCreateDTO) -> Action:
        """
        Prepares a new action with data validation and parsing.
        """
        # TODO: other rules
        parsed = self._parser.parse_action(action_in.raw_action_code)

        if action_in.sequence_in_rally is None or action_in.sequence_in_rally <= 0:
            raise BadRequestError(
                "sequence_in_rally must be a positive integer",
                code="MISSING_SEQUENCE",
                details={},
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
                },
            )

        payload = action_in.model_copy(
            update={
                "team_context": parsed.team_context,
                "skill_code": parsed.skill_code,
                "evaluation_code": parsed.evaluation_code,
                "player_jersey_number": parsed.player_jersey_number,
                "start_zone": parsed.start_zone,
                "start_subzone": parsed.start_subzone,
                "end_zone": parsed.end_zone,
                "end_subzone": parsed.end_subzone,
                "modifiers": "".join(parsed.modifiers) if parsed.modifiers else None,
            }
        )

        return self.action_crud.create(db=db, obj_in=payload)

    def update(
        self, db: Session, action_id: UUID, action_in: ActionUpdateDTO
    ) -> Action:
        db_action = self.get_by_id(db=db, action_id=action_id)

        if action_in.raw_action_code:
            parsed = self._parser.parse_action(action_in.raw_action_code)
            action_in = action_in.model_copy(
                update={
                    "team_context": parsed.team_context,
                    "skill_code": parsed.skill_code,
                    "evaluation_code": parsed.evaluation_code,
                    "player_jersey_number": parsed.player_jersey_number,
                    "start_zone": parsed.start_zone,
                    "start_subzone": parsed.start_subzone,
                    "end_zone": parsed.end_zone,
                    "end_subzone": parsed.end_subzone,
                    "modifiers": "".join(parsed.modifiers)
                    if parsed.modifiers
                    else None,
                }
            )

        data = action_in.model_dump(exclude_unset=True)
        if ("rally_id" in data) or ("sequence_in_rally" in data):
            rally_id = data.get("rally_id", db_action.rally_id)
            seq = data.get("sequence_in_rally", db_action.sequence_in_rally)
            existing = self.action_crud.get_by_rally_id_and_sequence(
                db, rally_id=rally_id, sequence=seq
            )
            if existing and existing.id != db_action.id:
                raise ConflictError(
                    "Sequence already used in this rally",
                    code="SEQUENCE_CONFLICT",
                    details={"rally_id": str(rally_id), "sequence_in_rally": seq},
                )

        return self.action_crud.update(db=db, db_obj=db_action, obj_in=action_in)

    def delete(self, db: Session, action_id: UUID) -> Action:
        db_action = self.get_by_id(db=db, action_id=action_id)

        return self.action_crud.remove(db=db, db_obj=db_action)
