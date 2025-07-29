from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .database import Base 

class Team(Base):
    __tablename__ = "teams"
    
    team_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    base_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String(3), nullable=False) # Odzwierciedla character varying(3)
    address = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    date_of_foundation = Column(Date, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    home_matches = relationship("Match", foreign_keys="[Match.home_team_id]", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="[Match.away_team_id]", back_populates="away_team")

class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)
    score = Column(String, nullable=True)
    status = Column(String, nullable=True)

    home_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id"))
    away_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id"))
    
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
