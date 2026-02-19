from uuid import UUID

from sqlmodel import Session

from app.crud.crud_lineup import CRUDLineup
from app.crud.crud_set_state import crud_set_state
from app.models.lineup import Lineup
from app.schemas.lineup import LineupCreateDTO


class LineupService:
    def __init__(self, lineup_crud: CRUDLineup):
        self.lineup_crud = lineup_crud

    def create_set_lineups(
        self, db: Session, set_id: UUID, payload: LineupCreateDTO
    ) -> list[Lineup]:

        # 1. Konwersja słownika pozycji na listę uporządkowaną [P1, P2... P6]
        # P1 to strefa 1 (zagrywająca), potem P2-P6
        home_order = [
            payload.home.positions["P1"],
            payload.home.positions["P2"],
            payload.home.positions["P3"],
            payload.home.positions["P4"],
            payload.home.positions["P5"],
            payload.home.positions["P6"],
        ]

        away_order = [
            payload.away.positions["P1"],
            payload.away.positions["P2"],
            payload.away.positions["P3"],
            payload.away.positions["P4"],
            payload.away.positions["P5"],
            payload.away.positions["P6"],
        ]

        # 2. Tworzymy rekordy Lineup (dla historii/protokołu)
        home_lineup = Lineup(
            set_id=set_id,
            team_id=payload.home.team_id,
            p1_id=home_order[0],
            p2_id=home_order[1],
            p3_id=home_order[2],
            p4_id=home_order[3],
            p5_id=home_order[4],
            p6_id=home_order[5],
            libero_id=payload.home.libero_id,
        )

        away_lineup = Lineup(
            set_id=set_id,
            team_id=payload.away.team_id,
            p1_id=away_order[0],
            p2_id=away_order[1],
            p3_id=away_order[2],
            p4_id=away_order[3],
            p5_id=away_order[4],
            p6_id=away_order[5],
            libero_id=payload.away.libero_id,
        )

        db.add(home_lineup)
        db.add(away_lineup)

        # 3. INICJALIZACJA SET_STATE
        # Ustalamy ID drużyny serwującej
        serving_team_id = (
            payload.home.team_id if payload.starting_server == "home"
            else payload.away.team_id
        )

        # Tworzymy stan początkowy seta
        # Zakładamy, że serving_index = 0 oznacza,
        # że serwuje zawodnik z pozycji P1 (indeks 0 w liście)
        crud_set_state.upsert_for_set(
            db,
            set_id=set_id,
            data={
                "serving_team_id": serving_team_id,
                "serving_index": 0, # Zawsze zaczyna P1
                "rotation_home": home_order,
                "rotation_away": away_order,
                "libero_home_id": payload.home.libero_id,
                "libero_away_id": payload.away.libero_id
            }
        )

        db.commit()
        db.refresh(home_lineup)
        db.refresh(away_lineup)

        return [home_lineup, away_lineup]
