from pydantic import BaseModel
from datetime import date
from uuid import UUID

import enum

# ==== Country schema ====

class CountryBase(BaseModel):
    code: str
    name: str

class CountryCreate(CountryBase):
    pass

class CountryUpdate(BaseModel):
    code: str | None = None
    name: str | None = None

class Country(CountryBase):
    class Config:
        from_attributes = True

# ==== Season schema ====

class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"

class SeasonBase(BaseModel):
    name: str
    season_type: SeasonType
    start_date: date
    end_date: date

class SeasonCreate(SeasonBase):
    pass

class SeasonUpdate(BaseModel):
    name: str | None = None
    season_type: SeasonType | None = None
    start_date: date | None = None
    end_date: date | None = None

class Season(SeasonBase):
    id: UUID
    class Config:
        from_attributes = True

# ==== Arena schema ====

class ArenaBase(BaseModel):
    name: str
    country_code: str
    city: str | None = None
    address: str | None = None
    capacity: int | None = None

class ArenaCreate(ArenaBase):
    pass

class ArenaUpdate(BaseModel):
    name: str | None = None
    country_code: str | None = None
    city: str | None = None
    address: str | None = None
    capacity: int | None = None

class Arena(ArenaBase):
    id: UUID

    class Config:
        from_attributes = True

# ==== Staff Member schema ====

class StaffRoleType(str, enum.Enum):
    head_coach = "head_coach"
    assistant = "assistant"

class StaffMemberBase(BaseModel):
    first_name: str
    last_name: str
    nationality_code: str
    role_type: StaffRoleType

class StaffMemberCreate(StaffMemberBase):
    pass

class StaffMemberUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    nationality_code: str | None = None
    role_type: StaffRoleType | None = None

class StaffMember(StaffMemberBase):
    id: UUID

    class Config:
        from_attributes = True

# ==== Player schema ====

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

class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    nationality_code: str
    height_cm: int | None = None
    weight_kg: int | None = None
    playing_position: PlayerPosition | None = None
    dominant_hand: PlayerHand | None = None
    spike_reach_cm: int | None = None
    block_reach_cm: int | None = None
    photo_url: str | None = None
    bio: str | None = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    nationality_code: str | None = None
    height_cm: int | None = None
    weight_kg: int | None = None
    playing_position: PlayerPosition | None = None
    dominant_hand: PlayerHand | None = None
    spike_reach_cm: int | None = None
    block_reach_cm: int | None = None
    photo_url: str | None = None
    bio: str | None = None

class Player(PlayerBase):
    id: UUID

    class Config:
        from_attributes = True

# ==== Team schema ====

class TeamType(str, enum.Enum):
    club = "club"
    national = "national"

class TeamBase(BaseModel):
    name: str
    team_type: TeamType
    country_code: str
    home_arena_id: UUID | None = None
    logo_url: str | None = None
    website_url: str | None = None
    email: str | None = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: str | None = None
    team_type: TeamType | None = None
    country_code: str | None = None
    home_arena_id: UUID | None = None
    logo_url: str | None = None
    website_url: str | None = None
    email: str | None = None

class Team(TeamBase):
    id: UUID

    class Config:
        from_attributes = True

# ==== Staff-Team History schema ====

class StaffTeamHistoryBase(BaseModel):
    staff_member_id: UUID
    team_id: UUID
    season_id: UUID
    role: str

class StaffTeamHistoryCreate(StaffTeamHistoryBase):
    pass

class StaffTeamHistoryUpdate(BaseModel):
    role: str | None = None

class StaffTeamHistory(StaffTeamHistoryBase):
    id: UUID
    
    class Config:
        from_attributes = True

# ==== Player-Team History schema ====

class PlayerTeamHistoryBase(BaseModel):
    player_id: UUID
    team_id: UUID
    season_id: UUID
    start_date: date
    end_date: date | None = None
    jersey_number: int | None = None

class PlayerTeamHistoryCreate(PlayerTeamHistoryBase):
    pass

class PlayerTeamHistoryUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    jersey_number: int | None = None

class PlayerTeamHistory(PlayerTeamHistoryBase):
    id: UUID

    class Config:
        from_attributes = True
