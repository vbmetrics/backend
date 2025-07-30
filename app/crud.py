from sqlalchemy.orm import Session
from . import models, schemas
from uuid import UUID


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

def get_season(db: Session, season_id: UUID):
    return db.query(models.Season).filter(models.Season.id == season_id).first()

def get_seasons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Season).offset(skip).limit(limit).all()

def create_season(db: Session, season: schemas.SeasonCreate):
    db_season = models.Season(**season.model_dump())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

def update_season(db: Session, season_id: UUID, season_update: schemas.SeasonUpdate):
    db_season = get_season(db, season_id=season_id)
    if not db_season:
        return None
    
    update_data = season_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_season, key, value)

    db.add(db_season)
    db.commit()
    db.refresh(db_season)

    return db_season

def delete_season(db: Session, season_id: UUID):
    db_season = get_season(db, season_id=season_id)
    if not db_season:
        return None
    
    db.delete(db_season)
    db.commit()
    
    return db_season

# ==== Arena CRUD ====

def get_arena(db: Session, arena_id: UUID):
    return db.query(models.Arena).filter(models.Arena.id == arena_id).first()

def get_arenas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Arena).offset(skip).limit(limit).all()

def create_arena(db: Session, arena: schemas.ArenaCreate):
    db_arena = models.Arena(**arena.model_dump())
    db.add(db_arena)
    db.commit()
    db.refresh(db_arena)
    return db_arena

def update_arena():
    return

def delete_arena():
    return
