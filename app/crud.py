from sqlalchemy.orm import Session
from . import models, schemas


# ==== Country CRUD ====

def get_country(db: Session, country_code: str):
    return db.query(models.Country).filter(models.Country.code == country_code).first()

def get_countries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Country).offset(skip).limit(limit).all()

def create_country(db: Session, country: schemas.CountryCreate):
    db_country = models.Country(code=country.code, name=country.name)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

# ==== Season CRUD ====

def get_season(db: Session, season_id: str):
    return db.query(models.Season).filter(models.Season.id == season_id).first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Season).offset(skip).limit(limit).all()

def create_season(db: Session, season: schemas.SeasonCreate):
    db_season = models.Season(**season.model_dump())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season
