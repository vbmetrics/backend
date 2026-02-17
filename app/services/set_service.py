from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session

from app.crud.crud_match import CRUDMatch
from app.crud.crud_match import match as match_crud
from app.crud.crud_set import CRUDSet
from app.crud.crud_set import vb_set as set_crud
from app.models.match import Match
from app.models.set import Set
from app.schemas import SetCreateDTO, SetUpdateDTO
from app.services.errors import BadRequestError, ConflictError, NotFoundError


class SetService:
    def __init__(
        self, set_crud_dep: CRUDSet = set_crud, match_crud_dep: CRUDMatch = match_crud
    ):
        self.set_crud = set_crud_dep
        self.match_crud = match_crud_dep

    # ------- helpers -------

    @staticmethod
    def _validate_scores(home: int | None, away: int | None) -> None:
        pass

    @staticmethod
    def _winner_from_scores(
        home_team_id: UUID, away_team_id: UUID, home: int | None, away: int | None
    ) -> UUID | None:
        # DODANE: Jeśli jest remis (np. 0:0 na starcie), nie ma zwycięzcy
        if home is None or away is None or home == away:
            return None
        return home_team_id if home > away else away_team_id

    @staticmethod
    def _validate_winner_is_participant(
        match: Match, winner_team_id: UUID | None
    ) -> None:
        if winner_team_id and winner_team_id not in {
            match.home_team_id,
            match.away_team_id,
        }:
            raise BadRequestError(
                "winner_team_id must be either match.home_team_id or match.away_team_id",  # noqa
                code="WINNER_NOT_A_PARTICIPANT",
            )

    # ------- CRUD -------

    def get_by_id(self, db: Session, set_id: UUID) -> Set:
        db_set = self.set_crud.get(db=db, id=set_id)
        if not db_set:
            raise NotFoundError(
                "Set not found", code="SET_NOT_FOUND", details={"set_id": str(set_id)}
            )
        return db_set

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        match_id: UUID | None = None,
        winner_team_id: UUID | None = None,
        set_number_from: int | None = None,
        set_number_to: int | None = None,
    ) -> Sequence[Set]:
        return self.set_crud.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            match_id=match_id,
            winner_team_id=winner_team_id,
            set_number_from=set_number_from,
            set_number_to=set_number_to,
        )

    def create(self, db: Session, set_in: SetCreateDTO) -> Set:
        if self.set_crud.get_by_match_and_number(
            db, match_id=set_in.match_id, set_number=set_in.set_number
        ):
            raise ConflictError(
                "Set number already exists in this match",
                code="SET_NUMBER_CONFLICT",
                details={
                    "match_id": str(set_in.match_id),
                    "set_number": set_in.set_number,
                },
            )

        match = self.match_crud.get(db=db, id=set_in.match_id)
        if not match:
            raise BadRequestError(
                "match_id does not exist",
                code="MATCH_NOT_FOUND",
                details={"match_id": str(set_in.match_id)},
            )

        self._validate_scores(set_in.home_team_score, set_in.away_team_score)
        inferred = self._winner_from_scores(
            match.home_team_id,
            match.away_team_id,
            set_in.home_team_score,
            set_in.away_team_score,
        )
        winner = set_in.winner_team_id or inferred
        self._validate_winner_is_participant(match, winner)

        payload = set_in.model_copy(update={"winner_team_id": winner})
        return self.set_crud.create(db=db, obj_in=payload)

    def update(self, db: Session, set_id: UUID, set_in: SetUpdateDTO) -> Set:
        db_set = self.get_by_id(db=db, set_id=set_id)

        match = self.match_crud.get(db=db, id=db_set.match_id)
        if not match:
            raise BadRequestError(
                "match_id does not exist",
                code="MATCH_NOT_FOUND",
                details={"match_id": str(db_set.match_id)},
            )

        data = set_in.model_dump(exclude_unset=True)
        home = data.get("home_team_score", db_set.home_team_score)
        away = data.get("away_team_score", db_set.away_team_score)
        winner = data.get("winner_team_id", db_set.winner_team_id)

        self._validate_scores(home, away)
        inferred = self._winner_from_scores(
            match.home_team_id, match.away_team_id, home, away
        )
        if winner is None:
            winner = inferred
        else:
            # if scores given, winner must agree
            if inferred is not None and winner != inferred:
                raise BadRequestError(
                    "winner_team_id disagrees with scores",
                    code="WINNER_SCORE_MISMATCH",
                    details={
                        "inferred_winner": str(inferred),
                        "winner_team_id": str(winner),
                    },
                )

        self._validate_winner_is_participant(match, winner)

        data["winner_team_id"] = winner
        return self.set_crud.update(db=db, db_obj=db_set, obj_in=data)

    def delete(self, db: Session, set_id: UUID) -> Set:
        db_set = self.get_by_id(db=db, set_id=set_id)

        return self.set_crud.remove(db=db, db_obj=db_set)
