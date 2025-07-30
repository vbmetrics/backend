from sqlalchemy import ( 
    Column, String, CHAR, Integer, Date, Enum as SQLAlchemyEnum,
    ForeignKey,
    CheckConstraint 
)
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
#from sqlalchemy.sql import func

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
