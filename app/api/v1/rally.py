from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.schemas import RallyCreateDTO, RallyReadDTO, RallyUpdateDTO
from app.services.rally_service import RallyService

router = APIRouter(prefix="/rally", tags=["Rally"])


@router.post("/", response_model=RallyReadDTO, status_code=status.HTTP_201_CREATED)
def create_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_in: RallyCreateDTO,
    service: RallyService = Depends(deps.get_rally_service),
):
    return service.create(db=db, rally_in=rally_in)


@router.get("/", response_model=list[RallyReadDTO])
def read_rallies_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    set_id: UUID | None = None,
    serve_team_id: UUID | None = None,
    score_team_id: UUID | None = None,
    rally_number_from: int | None = None,
    rally_number_to: int | None = None,
    service: RallyService = Depends(deps.get_rally_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        set_id=set_id,
        serve_team_id=serve_team_id,
        score_team_id=score_team_id,
        rally_number_from=rally_number_from,
        rally_number_to=rally_number_to,
    )


@router.get("/{rally_id}", response_model=RallyReadDTO)
def read_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_id: UUID,
    service: RallyService = Depends(deps.get_rally_service),
):
    return service.get_by_id(db=db, rally_id=rally_id)


@router.patch("/{rally_id}", response_model=RallyReadDTO)
def update_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_id: UUID,
    rally_in: RallyUpdateDTO,
    service: RallyService = Depends(deps.get_rally_service),
):
    return service.update(db=db, rally_id=rally_id, rally_in=rally_in)


@router.delete("/{rally_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_id: UUID,
    service: RallyService = Depends(deps.get_rally_service),
):
    service.delete(db=db, rally_id=rally_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
