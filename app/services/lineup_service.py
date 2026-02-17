from uuid import UUID

from sqlmodel import Session

from app.crud.crud_lineup import CRUDLineup
from app.models.lineup import Lineup
from app.schemas.lineup import LineupCreateDTO


class LineupService:
    def __init__(self, lineup_crud: CRUDLineup):
        self.lineup_crud = lineup_crud

    def create_set_lineups(
        self, db: Session, set_id: UUID, payload: LineupCreateDTO
    ) -> list[Lineup]:

        # 1. Tworzymy skład gospodarzy
        home_lineup = Lineup(
            set_id=set_id,
            team_id=payload.home.team_id,
            p1_id=payload.home.positions["P1"],
            p2_id=payload.home.positions["P2"],
            p3_id=payload.home.positions["P3"],
            p4_id=payload.home.positions["P4"],
            p5_id=payload.home.positions["P5"],
            p6_id=payload.home.positions["P6"],
            libero_id=payload.home.libero_id,
        )

        # 2. Tworzymy skład gości
        away_lineup = Lineup(
            set_id=set_id,
            team_id=payload.away.team_id,
            p1_id=payload.away.positions["P1"],
            p2_id=payload.away.positions["P2"],
            p3_id=payload.away.positions["P3"],
            p4_id=payload.away.positions["P4"],
            p5_id=payload.away.positions["P5"],
            p6_id=payload.away.positions["P6"],
            libero_id=payload.away.libero_id,
        )

        db.add(home_lineup)
        db.add(away_lineup)
        db.commit()

        db.refresh(home_lineup)
        db.refresh(away_lineup)

        return [home_lineup, away_lineup]
