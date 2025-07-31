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

def update_arena(db: Session, arena_id: UUID, arena_update: schemas.ArenaUpdate):
    db_arena = get_arena(db, arena_id=arena_id)
    if not db_arena:
        return None
    
    update_data = arena_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_arena, key, value)

    db.add(db_arena)
    db.commit()
    db.refresh(db_arena)

    return db_arena

def delete_arena(db: Session, arena_id: UUID):
    db_arena = get_arena(db, arena_id=arena_id)
    if not db_arena:
        return None
    
    db.delete(db_arena)
    db.commit()
    
    return db_arena

# ==== Staff Member CRUD ====

def get_staff_member(db: Session, staff_member_id: UUID):
    return db.query(models.StaffMember).filter(models.StaffMember.id == staff_member_id).first()

def get_staff_members(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.StaffMember).offset(skip).limit(limit).all()

def create_staff_member(db: Session, staff_member: schemas.StaffMemberCreate):
    db_staff_member = models.StaffMember(**staff_member.model_dump())
    db.add(db_staff_member)
    db.commit()
    db.refresh(db_staff_member)
    return db_staff_member

def update_staff_member(db: Session, staff_member_id: UUID, staff_member_update: schemas.StaffMemberUpdate):
    db_staff_member = get_staff_member(db, staff_member_id=staff_member_id)
    if not db_staff_member:
        return None
    
    update_data = staff_member_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_staff_member, key, value)

    db.add(db_staff_member)
    db.commit()
    db.refresh(db_staff_member)

    return db_staff_member

def delete_staff_member(db: Session, staff_member_id: UUID):
    db_staff_member = get_staff_member(db, staff_member_id=staff_member_id)
    if not db_staff_member:
        return None
    
    db.delete(db_staff_member)
    db.commit()
    
    return db_staff_member

# ==== Player CRUD ====

def get_player(db: Session, player_id: UUID):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, player_id: UUID, player_update: schemas.PlayerUpdate):
    db_player = get_player(db, player_id=player_id)
    if not db_player:
        return None
    
    update_data = player_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_player, key, value)

    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player

def delete_player(db: Session, player_id: UUID):
    db_player = get_player(db, player_id=player_id)
    if not db_player:
        return None
    
    db.delete(db_player)
    db.commit()
    
    return db_player

# ==== Team CRUD ====

# TODO

# ==== Player-Team History CRUD ====

# TODO
