from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app import models
from app.api import deps
from app.services import country_service

router = APIRouter(
    prefix="/country",
    tags=["Country"],
)


@router.post(
    "/", response_model=models.CountryRead, status_code=status.HTTP_201_CREATED
)
def create_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_in: models.CountryCreate,
):
    return country_service.create(db=db, country_in=country_in)


@router.get("/", response_model=list[models.CountryRead])
def read_countries_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return country_service.get_all(db=db, skip=skip, limit=limit)


@router.get("/{country_code}", response_model=models.CountryRead)
def read_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_code: str,
):
    return country_service.get_by_code(db=db, country_code=country_code)


@router.patch("/{country_code}", response_model=models.CountryRead)
def update_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_code: str,
    country_in: models.CountryUpdate,
):
    return country_service.update(
        db=db, country_code=country_code, country_in=country_in
    )


@router.delete("/{country_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    country_code: str,
):
    country_service.delete(db=db, country_code=country_code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
