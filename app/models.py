from sqlalchemy import ( 
    Column, String, CHAR, Integer, Date, Enum as SQLAlchemyEnum,
    ForeignKey,
    CheckConstraint 
)
from sqlalchemy.dialects.postgresql import UUID

import uuid
import enum

from .database import Base 

class Country(Base):
    __tablename__ = "countries"

    code = Column(CHAR(2), primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"

class Season(Base):
    __tablename__ = "seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    season_type = Column("type", SQLAlchemyEnum(SeasonType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

class Arena(Base):
    __tablename__ = "arenas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    city = Column(String)
    address = Column(String)
    capacity = Column(Integer)
    country_code = Column(CHAR(2), ForeignKey("countries.code"), nullable=False)

    __table_args__ = (
        CheckConstraint('capacity > 0', name='positive_capacity'),
    )

class StaffRoleType(str, enum.Enum):
    head_coach = "head_coach"
    assistant = "assistant"

class StaffMember(Base):
    __tablename__ = "staff_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    nationality_code = Column(CHAR(2), ForeignKey("countries.code"), nullable=False)
    role_type = Column(SQLAlchemyEnum(StaffRoleType), nullable=False)

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

class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    nationality_code = Column(CHAR(2), ForeignKey("countries.code"), nullable=False)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    playing_position = Column(SQLAlchemyEnum(PlayerPosition))
    dominant_hand = Column(SQLAlchemyEnum(PlayerHand))
    spike_reach_cm = Column(Integer)
    block_reach_cm = Column(Integer)
    photo_url = Column(String)
    bio = Column(String)

    __table_args__ = (
        CheckConstraint('height_cm > 0', name='positive_height'),
        CheckConstraint('weight_cm > 0', name='positive_weight'),
        CheckConstraint('spike_reach_cm > 0', name='positive_spike_reach'),
        CheckConstraint('block_reach_cm > 0', name='positive_block_reach'),
    )

class TeamType(str, enum.Enum):
    club = "club"
    national = "national"

class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    team_type = Column("team_type", SQLAlchemyEnum(TeamType), nullable=False)
    country_code = Column(CHAR(2), ForeignKey("countries.code"), nullable=False)
    home_arena_id = Column(UUID(as_uuid=True), ForeignKey("arenas.id"), nullable=True)
    logo_url = Column(String)
    website_url = Column(String)
    email = Column(String)

class StaffTeamHistory(Base):
    __tablename__ = "staff_team_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String, nullable=False)
    staff_member_id = Column(UUID(as_uuid=True), ForeignKey("staff_members.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id"), nullable=False)
