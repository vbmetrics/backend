from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import rally_service

router = APIRouter(prefix="/rally", tags=["Rally"])


@router.post("/", response_model=models.RallyRead, status_code=status.HTTP_201_CREATED)
def create_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_in: models.RallyCreate,
):
    return rally_service.create(db=db, rally_in=rally_in)


@router.get("/", response_model=list[models.RallyRead])
def read_rallies_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 0,
    set_id: UUID | None = None,
    serve_team_id: UUID | None = None,
    score_team_id: UUID | None = None,
):
    return rally_service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        set_id=set_id,
        serve_team_id=serve_team_id,
        score_team_id=score_team_id,
    )


@router.get("/{rally_id}", response_model=models.RallyRead)
def read_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_id: UUID,
):
    return rally_service.get_by_id(db=db, rally_id=rally_id)


@router.patch("/{rally_id}", response_model=models.RallyRead)
def update_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_id: UUID,
    rally_in: models.RallyUpdate,
):
    return rally_service.update(db=db, rally_id=rally_id, rally_in=rally_in)


@router.delete("/{rally_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rally_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    rally_id: UUID,
):
    rally_service.delete(db=db, rally_id=rally_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
