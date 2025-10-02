from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.schemas import SetCreateDTO, SetReadDTO, SetUpdateDTO
from app.services.set_service import SetService

router = APIRouter(prefix="/set", tags=["Set"])


@router.post("/", response_model=SetReadDTO, status_code=status.HTTP_201_CREATED)
def create_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_in: SetCreateDTO,
    service: SetService = Depends(deps.get_set_service),
):
    return service.create(db=db, set_in=set_in)


@router.get("/", response_model=list[SetReadDTO])
def read_sets_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    match_id: UUID | None = None,
    winner_team_id: UUID | None = None,
    set_number_from: int | None = None,
    set_number_to: int | None = None,
    service: SetService = Depends(deps.get_set_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        match_id=match_id,
        winner_team_id=winner_team_id,
        set_number_from=set_number_from,
        set_number_to=set_number_to,
    )


@router.get("/{set_id}", response_model=SetReadDTO)
def read_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
    service: SetService = Depends(deps.get_set_service),
):
    return service.get_by_id(db=db, set_id=set_id)


@router.patch("/{set_id}", response_model=SetReadDTO)
def update_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
    set_in: SetUpdateDTO,
    service: SetService = Depends(deps.get_set_service),
):
    return service.update(db=db, set_id=set_id, set_in=set_in)


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    set_id: UUID,
    service: SetService = Depends(deps.get_set_service),
):
    service.delete(db=db, set_id=set_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
