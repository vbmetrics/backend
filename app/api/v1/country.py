from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api.deps import get_current_active_user, get_db, require_role
from app.models.user import UserRole
from app.services import country_service

router = APIRouter(
    prefix="/country",
    tags=["Country"],
)


@router.post(
    "/",
    response_model=models.CountryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_country_endpoint(
    *,
    db: Session = Depends(get_db),
    country_in: models.CountryCreate,
):
    """Create a new country record."""
    return country_service.create(db=db, country_in=country_in)


@router.get(
    "/",
    response_model=list[models.CountryRead],
    dependencies=[Depends(get_current_active_user)],
)
def read_countries_endpoint(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """Read all records from country table."""
    return country_service.get_all(db=db, skip=skip, limit=limit)


@router.get(
    "/{country_code}",
    response_model=models.CountryRead,
    dependencies=[Depends(get_current_active_user)],
)
def read_country_endpoint(
    *,
    db: Session = Depends(get_db),
    country_code: str,
):
    """Read a record with given alpha_2_code value."""
    return country_service.get_by_code(db=db, country_code=country_code)


@router.patch(
    "/{country_code}",
    response_model=models.CountryRead,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def update_country_endpoint(
    *,
    db: Session = Depends(get_db),
    country_code: str,
    country_in: models.CountryUpdate,
):
    """Update country record with given alpha_2_code value."""
    return country_service.update(
        db=db, country_code=country_code, country_in=country_in
    )


@router.delete(
    "/{country_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def delete_country_endpoint(
    *,
    db: Session = Depends(get_db),
    country_code: str,
):
    """Remove a record with given alpha_2_code value."""
    country_service.delete(db=db, country_code=country_code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
