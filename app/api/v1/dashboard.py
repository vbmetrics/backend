from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api import deps
from app.schemas.analytics import DashboardStatsDTO
from app.services.analytics_service import MatchAnalyticsService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

analytics_service = MatchAnalyticsService()

@router.get(
    "/stats",
    response_model=DashboardStatsDTO,
    dependencies=[Depends(deps.get_current_active_user)]
)
def get_dashboard_stats(
    team_id: UUID = Query(..., description="ID zespołu do analizy"),
    season_id: Optional[UUID] = Query(None, description="Opcjonalne ID sezonu"),
    db: Session = Depends(deps.get_db),
):
    """
    Zwraca zagregowane wskaźniki (Side-out%, Break Point%)
    oraz najlepszych zawodników wybranego zespołu.
    """
    return analytics_service.generate_dashboard_stats(
        db=db, team_id=team_id, season_id=season_id
    )
