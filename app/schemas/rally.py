from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RallyInputDTO(BaseModel):
    """To wysyła frontend: tylko kod, ID meczu i opcjonalnie komentarz."""
    raw_rally_code: str
    match_id: UUID
    comment: Optional[str] = None


class RallyBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rally_number_in_set: int = Field(gt=0, description="Rally number within the set.")
    raw_rally_code: str = Field(max_length=256)
    comment: Optional[str] = None

    set_id: UUID
    serve_team_id: UUID
    score_team_id: UUID


class RallyCreateDTO(RallyBaseDTO):
    """Payload to create Rally."""


class RallyUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_rally_code: Optional[str] = Field(default=None, max_length=256)
    comment: Optional[str] = None
    serve_team_id: Optional[UUID] = None
    score_team_id: Optional[UUID] = None
    rally_number_in_set: Optional[int] = Field(default=None, gt=0)
    set_id: Optional[UUID] = None


class RallyReadDTO(RallyBaseDTO):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
