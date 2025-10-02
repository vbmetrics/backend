from collections.abc import Sequence
from typing import Any, Optional, cast
from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlmodel import Session

from app.crud.crud_action import CRUDAction
from app.crud.crud_action import action as action_crud
from app.crud.crud_rally import CRUDRally
from app.crud.crud_rally import rally as rally_crud
from app.models.action import Action
from app.models.rally import Rally
from app.schemas import ActionCreateDTO, RallyCreateDTO, RallyUpdateDTO
from app.services.errors import ConflictError, NotFoundError
from app.utils.code_parser import CodeParser


class RallyService:
    def __init__(
        self,
        rally_crud_dep: CRUDRally = rally_crud,
        action_crud_dep: CRUDAction = action_crud,
        parser: Optional[CodeParser] = None,
    ):
        self.rally_crud = rally_crud_dep
        self.action_crud = action_crud_dep
        self._parser = parser or CodeParser()

    # ---------- helpers ----------

    def _ensure_unique_number(
        self,
        db: Session,
        *,
        set_id: UUID,
        rally_number_in_set: int,
        exclude_id: UUID | None = None,
    ) -> None:
        existing = self.rally_crud.get_by_set_id_and_rally_number(
            db, set_id=set_id, rally_number_in_set=rally_number_in_set
        )
        if existing and (exclude_id is None or existing.id != exclude_id):
            raise ConflictError(
                "rally_number_in_set already exists within this set",
                code="RALLY_NUMBER_CONFLICT",
                details={
                    "set_id": str(set_id),
                    "rally_number_in_set": rally_number_in_set,
                },
            )

    def _upsert_actions_from_raw(
        self, db: Session, *, rally_id: UUID, raw_rally_code: str
    ) -> str | None:
        """
        Parses raw rally code and (re)writes related Action rows with correct sequences.
        Returns parsed comment (if any) to be stored on Rally.comment.
        """
        parsed = self._parser.parse_rally(raw_rally_code)

        rally_col: Any = Action.rally_id
        del_stmt = sa_delete(Action).where(rally_col == rally_id)
        db.exec(cast(Any, del_stmt))
        db.commit()

        for idx, pa in enumerate(parsed.actions, start=1):
            dto = ActionCreateDTO(
                sequence_in_rally=idx,
                raw_action_code=pa.raw_action_code,
                team_context=pa.team_context,
                skill_code=pa.skill_code,
                evaluation_code=pa.evaluation_code,
                player_jersey_number=pa.player_jersey_number,
                start_zone=pa.start_zone,
                start_subzone=pa.start_subzone,
                end_zone=pa.end_zone,
                end_subzone=pa.end_subzone,
                modifiers="".join(pa.modifiers) if pa.modifiers else None,
                rally_id=rally_id,
                player_id=None,
            )
            self.action_crud.create(db=db, obj_in=dto)

        return parsed.comment

    # ---------- CRUD with parsing ----------

    def get_by_id(self, db: Session, rally_id: UUID) -> Rally:
        db_rally = self.rally_crud.get(db=db, id=rally_id)
        if not db_rally:
            raise NotFoundError(
                "Rally not found",
                code="RALLY_NOT_FOUND",
                details={"rally_id": str(rally_id)},
            )
        return db_rally

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        set_id: UUID | None = None,
        serve_team_id: UUID | None = None,
        score_team_id: UUID | None = None,
        rally_number_from: int | None = None,
        rally_number_to: int | None = None,
    ) -> Sequence[Rally]:
        return self.rally_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            set_id=set_id,
            serve_team_id=serve_team_id,
            score_team_id=score_team_id,
            rally_number_from=rally_number_from,
            rally_number_to=rally_number_to,
        )

    def create(self, db: Session, rally_in: RallyCreateDTO) -> Rally:
        # Uniqueness in (set_id, rally_number_in_set)
        self._ensure_unique_number(
            db, set_id=rally_in.set_id, rally_number_in_set=rally_in.rally_number_in_set
        )

        # Create rally first
        rally = self.rally_crud.create(db=db, obj_in=rally_in)

        # Parse and create actions,
        # fill comment if present (unless client already set it)
        parsed_comment = self._upsert_actions_from_raw(
            db,
            rally_id=rally.id,  # type: ignore[arg-type]
            raw_rally_code=rally_in.raw_rally_code,
        )
        if parsed_comment and not rally.comment:
            rally.comment = parsed_comment
            db.add(rally)
            db.commit()
            db.refresh(rally)

        return rally

    def update(self, db: Session, rally_id: UUID, rally_in: RallyUpdateDTO) -> Rally:
        rally = self.get_by_id(db=db, rally_id=rally_id)

        # If either set_id or rally_number_in_set is changing, re-check uniqueness
        data = rally_in.model_dump(exclude_unset=True)
        if "set_id" in data or "rally_number_in_set" in data:
            set_id = data.get("set_id", rally.set_id)
            num = data.get("rally_number_in_set", rally.rally_number_in_set)
            self._ensure_unique_number(
                db, set_id=set_id, rally_number_in_set=num, exclude_id=rally.id
            )

        # If raw code changes, re-parse & rewrite actions,
        # capture (new) parsed comment if provided
        parsed_comment: Optional[str] = None
        if "raw_rally_code" in data and data["raw_rally_code"]:
            assert rally.id is not None, "Existing Rally should have a non-null id"
            rally_id_value: UUID = rally.id
            parsed_comment = self._upsert_actions_from_raw(
                db, rally_id=rally_id_value, raw_rally_code=data["raw_rally_code"]
            )

        # If server-side parsed comment exists
        # and client didn't explicitly set comment, apply parsed
        if parsed_comment is not None and "comment" not in data:
            data["comment"] = parsed_comment

        # Persist rally fields
        return self.rally_crud.update(db=db, db_obj=rally, obj_in=data)

    def delete(self, db: Session, rally_id: UUID) -> Rally:
        rally = self.get_by_id(db=db, rally_id=rally_id)

        assert rally.id is not None, "Existing Rally should have a non-null id"
        rally_id_value: UUID = rally.id
        rally_col: Any = Action.rally_id
        del_stmt = sa_delete(Action).where(rally_col == rally_id_value)
        db.exec(cast(Any, del_stmt))
        db.commit()

        return self.rally_crud.remove(db=db, db_obj=rally)
