from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api import deps
from app.schemas.analytics import MatchReportDTO
from app.services.analytics_service import MatchAnalyticsService

router = APIRouter(
    prefix="/match/{match_id}/analytics",
    tags=["Analytics"],
)

# Inicjalizacja serwisu
analytics_service = MatchAnalyticsService()

@router.get(
    "/report",
    response_model=MatchReportDTO,
    dependencies=[Depends(deps.get_current_active_user)]
)
def get_match_report_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    match_id: UUID,
):
    """
    Generuje i zwraca pełny raport statystyczny z meczu
    (Box Score i statystyki drużynowe).
    """
    return analytics_service.generate_report(db=db, match_id=match_id)
