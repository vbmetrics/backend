from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.user import UserRole
from app.schemas import ArenaCreateDTO, ArenaReadDTO, ArenaUpdateDTO
from app.services.arena_service import ArenaService

router = APIRouter(
    prefix="/arena",
    tags=["Arena"],
)


@router.post(
    "/",
    response_model=ArenaReadDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def create_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_in: ArenaCreateDTO,
    service: ArenaService = Depends(deps.get_arena_service),
):
    return service.create(db=db, arena_in=arena_in)


@router.get(
    "/",
    response_model=list[ArenaReadDTO],
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_arenas_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    country_code: str | None = None,
    city: str | None = None,
    search: str | None = None,
    service: ArenaService = Depends(deps.get_arena_service),
):
    return service.get_all(
        db=db,
        skip=skip,
        limit=limit,
        country_code=country_code,
        city=city,
        search=search
    )


@router.get(
    "/{arena_id}",
    response_model=ArenaReadDTO,
    dependencies=[Depends(deps.get_current_active_user)]
)
def read_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_id: UUID,
    service: ArenaService = Depends(deps.get_arena_service),
):
    return service.get_by_id(db=db, arena_id=arena_id)


@router.patch(
    "/{arena_id}",
    response_model=ArenaReadDTO,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def update_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_id: UUID,
    arena_in: ArenaUpdateDTO,
    service: ArenaService = Depends(deps.get_arena_service),
):
    return service.update(db=db, arena_id=arena_id, arena_in=arena_in)


@router.delete(
    "/{arena_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.require_role(UserRole.admin))]
)
def delete_arena_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    arena_id: UUID,
    service: ArenaService = Depends(deps.get_arena_service),
):
    service.delete(db=db, arena_id=arena_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
