from sqlalchemy import Column, String, CHAR, Date, Enum as SQLAlchemyEnum   # DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy.orm import relationship
#from sqlalchemy.sql import func

import uuid
import enum

from .database import Base 

class SeasonType(str, enum.Enum):
    club = "club"
    national = "national"

class Country(Base):
    __tablename__ = "countries"

    code = Column(CHAR(2), primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

class Season(Base):
    __tablename__ = "seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    type = Column(SQLAlchemyEnum(SeasonType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
