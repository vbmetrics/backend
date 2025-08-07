from sqlmodel import Session, select, selectinload
from uuid import UUID

from . import models


# COUNTRY CRUD

def get_country(session: Session, country_code: str) -> models.Country | None:
    return session.get(models.Country, country_code)

def get_countries(session: Session, skip: int = 0, limit: int = 100) -> list[models.Country]:
    statement = select(models.Country).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_country(session: Session, country: models.CountryCreate) -> models.Country:
    db_country = models.Country.model_validate(country)
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country

def update_country(session: Session, db_country: models.Country, country_update: models.CountryUpdate) -> models.Country:
    update_data = country_update.model_dump(exclude_unset=True)
    db_country.sqlmodel_update(update_data)
    
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country

def delete_country(session: Session, db_country: models.Country) -> None:
    session.delete(db_country)
    session.commit()
    return

# SEASON CRUD

def get_season(session: Session, season_id: UUID) -> models.Season | None:
    return session.get(models.Season, season_id)

def get_seasons(session: Session, skip: int = 0, limit: int = 100) -> list[models.Season]:
    statement = select(models.Season).offset(skip).limit(limit)
    results = session.exec(statement)
    return results.all()

def create_season(session: Session, season: models.SeasonCreate) -> models.Season:
    db_season = models.Season.model_validate(season)
    session.add(db_season)
    session.commit()
    session.refresh(db_season)
    return db_season

def update_season(session: Session, db_season: models.Season, season_update: models.SeasonUpdate) -> models.Season:
    update_data = season_update.model_dump(exclude_unset=True)
    db_season.sqlmodel_update(update_data)
    
    session.add(db_season)
    session.commit()
    session.refresh(db_season)
    return db_season

def delete_season(session: Session, db_season: models.Season) -> None:
    session.delete(db_season)
    session.commit()
    return

# ARENA CRUD

def get_arena(session: Session, arena_id: UUID) -> models.Arena | None:
    statement = select(models.Arena).where(models.Arena.id == arena_id).options(selectinload(models.Arena.country))
    return session.exec(statement).first()

def get_arenas(session: Session, skip: int = 0, limit: int = 100) -> list[models.Arena]:
    statement = select(models.Arena).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_arena(session: Session, arena: models.ArenaCreate) -> models.Arena:
    db_arena = models.Arena.model_validate(arena)
    session.add(db_arena)
    session.commit()
    session.refresh(db_arena)
    return db_arena

def update_arena(session: Session, db_arena: models.Arena, arena_update: models.ArenaUpdate) -> models.Arena:
    update_data = arena_update.model_dump(exclude_unset=True)
    db_arena.sqlmodel_update(update_data)
    
    session.add(db_arena)
    session.commit()
    session.refresh(db_arena)
    return db_arena

def delete_arena(session: Session, db_arena: models.Arena) -> None:
    session.delete(db_arena)
    session.commit()
    return

# STAFF MEMBER CRUD

def get_staff_member(session: Session, staff_member_id: UUID) -> models.StaffMember | None:
    statement = select(models.StaffMember).where(models.StaffMember.id == staff_member_id).options(selectinload(models.StaffMember.nationality))
    return session.exec(statement).first()

def get_staff_members(session: Session, skip: int = 0, limit: int = 100) -> list[models.StaffMember]:
    statement = select(models.StaffMember).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_staff_member(session: Session, staff_member: models.StaffMemberCreate) -> models.StaffMember:
    db_staff_member = models.StaffMember.model_validate(staff_member)
    session.add(db_staff_member)
    session.commit()
    session.refresh(db_staff_member)
    return db_staff_member

def update_staff_member(session: Session, db_staff_member: models.StaffMember, staff_member_update: models.StaffMemberUpdate) -> models.StaffMember:
    update_data = staff_member_update.model_dump(exclude_unset=True)
    db_staff_member.sqlmodel_update(update_data)
    
    session.add(db_staff_member)
    session.commit()
    session.refresh(db_staff_member)
    return db_staff_member

def delete_staff_member(session: Session, db_staff_member: models.StaffMember) -> None:
    session.delete(db_staff_member)
    session.commit()
    return

# PLAYER CRUD

def get_player(session: Session, player_id: UUID) -> models.Player | None:
    statement = select(models.Player).where(models.Player.id == player_id).options(selectinload(models.Player.nationality))
    return session.exec(statement).first()

def get_players(session: Session, skip: int = 0, limit: int = 100) -> list[models.Player]:
    statement = select(models.Player).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_player(session: Session, player: models.PlayerCreate) -> models.Player:
    db_player = models.Player.model_validate(player)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player

def update_player(session: Session, db_player: models.Player, player_update: models.PlayerUpdate) -> models.Player:
    update_data = player_update.model_dump(exclude_unset=True)
    db_player.sqlmodel_update(update_data)
    
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player

def delete_player(session: Session, db_player: models.Player) -> None:
    session.delete(db_player)
    session.commit()
    return

# TEAM CRUD

def get_team(session: Session, team_id: UUID) -> models.Team | None:
    statement = (
        select(models.Team)
        .where(models.Team.id == team_id)
        .options(
            selectinload(models.Team.country), 
            selectinload(models.Team.home_arena)
        )
    )
    return session.exec(statement).first()

def get_teams(session: Session, skip: int = 0, limit: int = 100) -> list[models.Team]:
    statement = select(models.Team).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_team(session: Session, team: models.TeamCreate) -> models.Team:
    db_team = models.Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

def update_team(session: Session, db_team: models.Team, team_update: models.TeamUpdate) -> models.Team:
    update_data = team_update.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(update_data)
    
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

def delete_team(session: Session, db_team: models.Team) -> None:
    session.delete(db_team)
    session.commit()
    return

# STAFF TEAM HISTORY CRUD

def get_staff_team_history(session: Session, history_id: UUID) -> models.StaffTeamHistory | None:
    statement = (
        select(models.StaffTeamHistory)
        .where(models.StaffTeamHistory.id == history_id)
        .options(
            selectinload(models.StaffTeamHistory.staff_member),
            selectinload(models.StaffTeamHistory.team),
            selectinload(models.StaffTeamHistory.season),
        )
    )
    return session.exec(statement).first()

def get_staff_team_histories(
    session: Session, 
    skip: int = 0, 
    limit: int = 100,
    staff_member_id: UUID | None = None,
    team_id: UUID | None = None,
    season_id: UUID | None = None,
) -> list[models.StaffTeamHistory]:
    statement = select(models.StaffTeamHistory)

    if staff_member_id:
        statement = statement.where(models.StaffTeamHistory.staff_member_id == staff_member_id)
    if team_id:
        statement = statement.where(models.StaffTeamHistory.team_id == team_id)
    if season_id:
        statement = statement.where(models.StaffTeamHistory.season_id == season_id)
    
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()

def create_staff_team_history(session: Session, history: models.StaffTeamHistoryCreate) -> models.StaffTeamHistory:
    db_history = models.StaffTeamHistory.model_validate(history)
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history

# PLAYER TEAM HISTORY CRUD

def get_player_team_history(session: Session, history_id: UUID) -> models.PlayerTeamHistory | None:
    statement = (
        select(models.PlayerTeamHistory)
        .where(models.PlayerTeamHistory.id == history_id)
        .options(
            selectinload(models.PlayerTeamHistory.player),
            selectinload(models.PlayerTeamHistory.team),
            selectinload(models.PlayerTeamHistory.season),
        )
    )
    return session.exec(statement).first()

def get_player_team_histories(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    player_id: UUID | None = None,
    team_id: UUID | None = None,
    season_id: UUID | None = None,
) -> list[models.PlayerTeamHistory]:
    statement = select(models.PlayerTeamHistory)

    if player_id:
        statement = statement.where(models.PlayerTeamHistory.player_id == player_id)
    if team_id:
        statement = statement.where(models.PlayerTeamHistory.team_id == team_id)
    if season_id:
        statement = statement.where(models.PlayerTeamHistory.season_id == season_id)
    
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()

def create_player_team_history(session: Session, history: models.PlayerTeamHistoryCreate) -> models.PlayerTeamHistory:
    db_history = models.PlayerTeamHistory.model_validate(history)
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history

def update_player_team_history(session: Session, db_history: models.PlayerTeamHistory, history_update: models.PlayerTeamHistoryUpdate) -> models.PlayerTeamHistory:
    update_data = history_update.model_dump(exclude_unset=True)
    db_history.sqlmodel_update(update_data)
    
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history
