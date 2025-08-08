import enum
import uuid
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlmodel import (
    Field,
    Relationship, 
    SQLModel, 
    Column,
    CheckConstraint
)

from sqlalchemy import CHAR
from sqlalchemy import Enum as SQLAlchemyEnum

# ========================================
# ENUM DEFINITIONS
# ========================================

class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"

class StaffRoleType(str, enum.Enum):
    head_coach = "head_coach"
    assistant = "assistant"

class PlayerPosition(str, enum.Enum):
    setter = "setter"
    opposite = "opposite"
    outside_hitter = "outside_hitter"
    middle_blocker = "middle_blocker"
    libero = "libero"

class PlayerHand(str, enum.Enum):
    right = "right"
    left = "left"
    ambidextrous = "ambidextrous"

class TeamType(str, enum.Enum):
    club = "club"
    national = "national"

# ========================================
# MODELS FOR BOTH DATABASE AND API
# ========================================

# COUNTRY

class CountryBase(SQLModel):
    name: str = Field(unique=True)
    alpha_2_code: str = Field(
        sa_column=Column(CHAR(2), primary_key=True, index=True)
    )
    latitude: float
    longitude: float

class Country(CountryBase, table=True):
    __tablename__ = "countries"

    # Relationships
    arenas: List["Arena"] = Relationship(back_populates="country")
    staff_members: List["StaffMember"] = Relationship(back_populates="nationality")
    players: List["Player"] = Relationship(back_populates="nationality")
    teams: List["Team"] = Relationship(back_populates="country")

class CountryCreate(CountryBase):
    pass

class CountryRead(CountryBase):
    pass

class CountryUpdate(SQLModel):
    name: Optional[str] = None

# SEASON

class SeasonBase(SQLModel):
    name: str = Field(unique=True)
    season_type: SeasonType = Field(
        sa_column=Column("type", SQLAlchemyEnum(SeasonType))
    )
    start_date: date
    end_date: date

class Season(SeasonBase, table=True):
    __tablename__ = "seasons"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    staff_team_histories: List["StaffTeamHistory"] = Relationship(back_populates="season")
    player_team_histories: List["PlayerTeamHistory"] = Relationship(back_populates="season")

class SeasonCreate(SeasonBase):
    pass

class SeasonRead(SeasonBase):
    id: UUID

class SeasonUpdate(SQLModel):
    name: Optional[str] = None
    season_type: Optional[SeasonType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

# ARENA

class ArenaBase(SQLModel):
    name: str
    city: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)
    country_code: str = Field(foreign_key="countries.alpha_2_code")

class Arena(ArenaBase, table=True):
    __tablename__ = "arenas"
    __table_args__ = (CheckConstraint('capacity > 0', name='positive_capacity'),)

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    country: Country = Relationship(back_populates="arenas")
    home_teams: List["Team"] = Relationship(back_populates="home_arena")

class ArenaCreate(ArenaBase):
    pass

class ArenaRead(ArenaBase):
    id: UUID

class ArenaReadWithCountry(ArenaRead):
    country: Optional[CountryRead] = None

class ArenaUpdate(SQLModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    country_code: Optional[str] = None

# STAFF MEMBER

class StaffMemberBase(SQLModel):
    first_name: str
    last_name: str
    role_type: StaffRoleType = Field(
        sa_column=Column(SQLAlchemyEnum(StaffRoleType))
    )
    nationality_code: str = Field(foreign_key="countries.alpha_2_code")

class StaffMember(StaffMemberBase, table=True):
    __tablename__ = "staff_members"
    
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    nationality: Country = Relationship(back_populates="staff_members")
    team_histories: List["StaffTeamHistory"] = Relationship(back_populates="staff_member")

class StaffMemberCreate(StaffMemberBase):
    pass

class StaffMemberRead(StaffMemberBase):
    id: UUID

class StaffMemberUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_type: Optional[StaffRoleType] = None
    nationality_code: Optional[str] = None

# PLAYER

class PlayerBase(SQLModel):
    first_name: str
    last_name: str
    date_of_birth: date
    height_cm: Optional[int] = Field(default=None, gt=0)
    weight_kg: Optional[int] = Field(default=None, gt=0)
    playing_position: Optional[PlayerPosition] = Field(default=None, sa_column=Column(SQLAlchemyEnum(PlayerPosition)))
    dominant_hand: Optional[PlayerHand] = Field(default=None, sa_column=Column(SQLAlchemyEnum(PlayerHand)))
    spike_reach_cm: Optional[int] = Field(default=None, gt=0)
    block_reach_cm: Optional[int] = Field(default=None, gt=0)
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    nationality_code: str = Field(foreign_key="countries.alpha_2_code")

class Player(PlayerBase, table=True):
    __tablename__ = "players"
    __table_args__ = (
        CheckConstraint('height_cm > 0', name='positive_height'),
        CheckConstraint('weight_kg > 0', name='positive_weight'),
        CheckConstraint('spike_reach_cm > 0', name='positive_spike_reach'),
        CheckConstraint('block_reach_cm > 0', name='positive_block_reach'),
    )

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    nationality: Country = Relationship(back_populates="players")
    team_histories: List["PlayerTeamHistory"] = Relationship(back_populates="player")

class PlayerCreate(PlayerBase):
    pass

class PlayerRead(PlayerBase):
    id: UUID

class PlayerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    playing_position: Optional[PlayerPosition] = None
    dominant_hand: Optional[PlayerHand] = None
    spike_reach_cm: Optional[int] = None
    block_reach_cm: Optional[int] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    nationality_code: Optional[str] = None

# TEAM

class TeamBase(SQLModel):
    name: str = Field(unique=True)
    team_type: TeamType = Field(
        sa_column=Column("team_type", SQLAlchemyEnum(TeamType))
    )
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    country_code: str = Field(foreign_key="countries.alpha_2_code")
    home_arena_id: Optional[UUID] = Field(default=None, foreign_key="arenas.id")

class Team(TeamBase, table=True):
    __tablename__ = "teams"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    country: Country = Relationship(back_populates="teams")
    home_arena: Optional[Arena] = Relationship(back_populates="home_teams")
    staff_histories: List["StaffTeamHistory"] = Relationship(back_populates="team")
    player_histories: List["PlayerTeamHistory"] = Relationship(back_populates="team")

class TeamCreate(TeamBase):
    pass

class TeamRead(TeamBase):
    id: UUID

class TeamUpdate(SQLModel):
    name: Optional[str] = None
    team_type: Optional[TeamType] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    country_code: Optional[str] = None
    home_arena_id: Optional[UUID] = None

# STAFF TEAM HISTORY

class StaffTeamHistoryBase(SQLModel):
    role: str
    staff_member_id: UUID = Field(foreign_key="staff_members.id")
    team_id: UUID = Field(foreign_key="teams.id")
    season_id: UUID = Field(foreign_key="seasons.id")

class StaffTeamHistory(StaffTeamHistoryBase, table=True):
    __tablename__ = "staff_team_history"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    staff_member: StaffMember = Relationship(back_populates="team_histories")
    team: Team = Relationship(back_populates="staff_histories")
    season: Season = Relationship(back_populates="staff_team_histories")

class StaffTeamHistoryCreate(StaffTeamHistoryBase):
    pass

class StaffTeamHistoryRead(StaffTeamHistoryBase):
    id: UUID

class StaffTeamHistoryReadWithDetails(StaffTeamHistoryRead):
    staff_member: Optional[StaffMemberRead] = None
    team: Optional[TeamRead] = None
    season: Optional[SeasonRead] = None

# PLAYER TEAM HISTORY

class PlayerTeamHistoryBase(SQLModel):
    start_date: date
    end_date: Optional[date] = None
    jersey_number: Optional[int] = Field(default=None, gt=0)

    # Foreign keys
    player_id: UUID = Field(foreign_key="players.id")
    team_id: UUID = Field(foreign_key="teams.id")
    season_id: UUID = Field(foreign_key="seasons.id")

class PlayerTeamHistory(PlayerTeamHistoryBase, table=True):
    __tablename__ = "player_team_history"

    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    player: Player = Relationship(back_populates="team_histories")
    team: Team = Relationship(back_populates="player_histories")
    season: Season = Relationship(back_populates="player_team_histories")

class PlayerTeamHistoryCreate(PlayerTeamHistoryBase):
    pass

class PlayerTeamHistoryRead(PlayerTeamHistoryBase):
    id: UUID

class PlayerTeamHistoryUpdate(SQLModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    jersey_number: Optional[int] = None

class PlayerTeamHistoryReadWithDetails(PlayerTeamHistoryRead):
    player: Optional["PlayerRead"] = None
    team: Optional["TeamRead"] = None
    season: Optional["SeasonRead"] = None
