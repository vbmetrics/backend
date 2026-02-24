# app/api/v1/match_flow.py
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api import deps
from app.schemas.lineup import LineupCreateDTO
from app.schemas.rally import RallyInputDTO
from app.schemas.state import MatchStateDTO
from app.services.live_service import LiveService

router = APIRouter(
    prefix="/match",
    tags=["Match Flow"],
)


@router.post(
    "/{match_id}/lineup",
    response_model=MatchStateDTO,
    status_code=status.HTTP_201_CREATED,
)
def set_initial_lineup_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    payload: LineupCreateDTO,
    service: LiveService = Depends(deps.get_live_service),
):
    """
    Inicjalizacja seta #1 i SetState (rotacje P1..P6 + libero + serwujący).
    Zwraca snapshot stanu zgodny z MatchStateDTO.
    """
    # LineupCreateDTO powinien zawierać:
    #   home: { team_id, positions{P1..P6}, libero_id? }
    #   away: { team_id, positions{P1..P6}, libero_id? }
    #   starting_server: "home" | "away"
    service.init_lineup(
        db=db,
        match_id=match_id,
        home=payload.home,
        away=payload.away,
        starting_server=payload.starting_server,
    )
    # po init weź świeży snapshot:
    return service.get_state(db=db, match_id=match_id)


@router.get("/{match_id}/state", response_model=MatchStateDTO)
def get_match_state_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    service: LiveService = Depends(deps.get_live_service),
):
    """
    Zwraca aktualny snapshot stanu meczu
    (wynik seta, sety, rotacje, serwujący, ostatnie rally).
    """
    return service.get_state(db=db, match_id=match_id)


@router.post(
    "/{match_id}/rally",
    response_model=MatchStateDTO,
    status_code=status.HTTP_201_CREATED,
)
def append_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    payload: RallyInputDTO,
    service: LiveService = Depends(deps.get_live_service),
):
    """
    Dodaje pojedynczy rally na podstawie kodu.
    """
    if payload.raw_rally_code.startswith("!"):
        return service.process_special_event(
            db, match_id, payload.raw_rally_code
        )

    return service.add_rally(
        db=db,
        match_id=match_id,
        code=payload.raw_rally_code,
        comment=payload.comment
    )


@router.get("/{match_id}/rallies")
def get_rallies_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    limit: int = 10,
    service: LiveService = Depends(deps.get_live_service),
):
    """
    Prosty podgląd ostatnich n rally (do debugowania / listowania).
    W v1 zwracamy to, co już zwraca get_state() w polu 'recent_rallies'.
    Jeśli potrzebujesz osobnego listowania – możemy dodać read-only w RallyService.
    """
    state = service.get_state(db=db, match_id=match_id)
    recent = state.get("recent_rallies", [])
    if limit and limit > 0:
        recent = recent[-limit:]
    return {"match_id": str(match_id), "recent_rallies": recent}

@router.delete(
    "/{match_id}/rally/last",
    response_model=MatchStateDTO,
)
def undo_last_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
    service: LiveService = Depends(deps.get_live_service),
):
    """
    Cofa ostatnią akcję w bieżącym secie.
    """
    return service.undo_last_rally(db=db, match_id=match_id)
