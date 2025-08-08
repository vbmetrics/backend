from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from .. import crud, models
from ..database import get_session


router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
)

@router.post("/", response_model=models.CountryRead, status_code=status.HTTP_201_CREATED)
def create_country(country: models.CountryCreate, session: Session = Depends(get_session)):
    db_country = crud.get_country(session, country_code=country.alpha_2_code)
    if db_country:
        raise HTTPException(status_code=400, detail="Country with this code already exists")
    return crud.create_country(session=session, country=country)

@router.get("/", response_model=List[models.CountryRead])
def read_countries(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return crud.get_countries(session=session, skip=skip, limit=limit)

@router.get("/{country_code}", response_model=models.CountryRead)
def read_country(country_code: str, session: Session = Depends(get_session)):
    db_country = crud.get_country(session=session, country_code=country_code)
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return db_country

@router.patch("/{country_code}", response_model=models.CountryRead)
def update_country(country_code: str, country_update: models.CountryUpdate, session: Session = Depends(get_session)):
    db_country = crud.get_country(session=session, country_code=country_code)
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return crud.update_country(session=session, db_country=db_country, country_update=country_update)

@router.delete("/{country_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_code: str, session: Session = Depends(get_session)):
    db_country = crud.get_country(session=session, country_code=country_code)
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    
    crud.delete_country(session=session, db_country=db_country)
    return
