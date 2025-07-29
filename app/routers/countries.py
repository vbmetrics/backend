from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/countries",
    tags=["Countries"]
)

@router.post("/", response_model=schemas.Country)
def create_country(country: schemas.CountryCreate, db: Session = Depends(get_db)):
    db_country = crud.get_country(db, country_code=country.code)
    if db_country:
        raise HTTPException(status_code=400, detail="Country with this code already exists")
    return crud.create_country(db=db, country=country)

@router.get("/", response_model=List[schemas.Country])
def read_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    countries = crud.get_countries(db, skip=skip, limit=limit)
    return countries

@router.get("/{country_code}", response_model=schemas.Country)
def read_country(country_code: str, db: Session = Depends(get_db)):
    db_country = crud.get_country(db, country_code=country_code)
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return db_country
