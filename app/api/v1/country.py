from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.api import deps
from app.models.user import UserRole
from app.schemas import CountryCreateDTO, CountryReadDTO, CountryUpdateDTO
from app.services.country_service import CountryService

router = APIRouter(
    prefix="/country",
    tags=["Country"],
)


@router.post(
    "/",
    response_model=CountryReadDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.require_role(UserRole.ADMIN))],
)
def create_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_in: CountryCreateDTO,
    service: CountryService = Depends(deps.get_country_service),
):
    return service.create(db=db, country_in=country_in)


@router.get(
    "/",
    response_model=list[CountryReadDTO],
    dependencies=[Depends(deps.get_current_active_user)],
)
def read_countries_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    service: CountryService = Depends(deps.get_country_service),
):
    return service.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{country_code}",
    response_model=CountryReadDTO,
    dependencies=[Depends(deps.get_current_active_user)],
)
def read_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_code: str,
    service: CountryService = Depends(deps.get_country_service),
):
    return service.get_by_code(db=db, country_code=country_code)


@router.patch(
    "/{country_code}",
    response_model=CountryReadDTO,
    dependencies=[Depends(deps.require_role(UserRole.ADMIN))],
)
def update_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_code: str,
    country_in: CountryUpdateDTO,
    service: CountryService = Depends(deps.get_country_service),
):
    return service.update(db=db, country_code=country_code, country_in=country_in)


@router.delete(
    "/{country_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(deps.require_role(UserRole.ADMIN))],
)
def delete_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_code: str,
    service: CountryService = Depends(deps.get_country_service),
):
    service.delete(db=db, country_code=country_code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
