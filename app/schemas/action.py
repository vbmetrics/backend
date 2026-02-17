from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActionBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sequence_in_rally: int = Field(gt=0, description="Action number in rally.")
    raw_action_code: str = Field(max_length=64)

    team_context: str = Field(min_length=1, max_length=1)  # 'H'|'G'
    skill_code: str = Field(min_length=1, max_length=1)  # 'S','R','P','A','B','D'
    evaluation_code: str = Field(min_length=1, max_length=1)  # '+','-','#'

    player_jersey_number: Optional[int] = Field(default=None, ge=0, le=99)
    start_zone: Optional[int] = Field(default=None, ge=1, le=9)
    end_zone: Optional[int] = Field(default=None, ge=1, le=9)
    start_subzone: Optional[str] = Field(
        default=None, min_length=1, max_length=1
    )  # 'A'..'D'
    end_subzone: Optional[str] = Field(
        default=None, min_length=1, max_length=1
    )  # 'A'..'D'
    modifiers: Optional[str] = Field(default=None, max_length=12)

    rally_id: UUID
    player_id: Optional[UUID] = None


class ActionCreateDTO(ActionBaseDTO):
    """Payload to create Action."""


class ActionUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_action_code: Optional[str] = Field(default=None, max_length=64)
    team_context: Optional[str] = Field(
        default=None, min_length=1, max_length=1
    )  # 'H'|'G'
    skill_code: Optional[str] = Field(
        default=None, min_length=1, max_length=1
    )  # 'S','R','P','A','B','D'
    evaluation_code: Optional[str] = Field(default=None, min_length=1, max_length=1)

    start_zone: Optional[int] = Field(default=None, ge=1, le=9)
    end_zone: Optional[int] = Field(default=None, ge=1, le=9)
    start_subzone: Optional[str] = Field(
        default=None, min_length=1, max_length=1
    )  # 'A'..'D'
    end_subzone: Optional[str] = Field(
        default=None, min_length=1, max_length=1
    )  # 'A'..'D'
    modifiers: Optional[str] = Field(default=None, max_length=12)
    player_jersey_number: Optional[int] = Field(default=None, ge=0, le=99)
    player_id: Optional[UUID] = None
    rally_id: Optional[UUID] = None
    sequence_in_rally: Optional[int] = Field(default=None, gt=0)


class ActionReadDTO(ActionBaseDTO):
    id: UUID


class ActionReadWithDetailsDTO(ActionReadDTO):
    # Extend later with nested DTOs for Rally/Player if desired
    pass
