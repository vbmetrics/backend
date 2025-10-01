# action
from .action import (
    ActionBaseDTO,
    ActionCreateDTO,
    ActionReadDTO,
    ActionReadWithDetailsDTO,
    ActionUpdateDTO,
)

# arena
from .arena import (
    ArenaBaseDTO,
    ArenaCreateDTO,
    ArenaReadDTO,
    ArenaUpdateDTO,
)
from .country import (
    CountryBaseDTO,
    CountryCreateDTO,
    CountryReadDTO,
    CountryUpdateDTO,
)

# player
from .player import (
    PlayerBaseDTO,
    PlayerCreateDTO,
    PlayerReadDTO,
    PlayerUpdateDTO,
)

# TODO
__all__ = [
    # action
    "ActionBaseDTO",
    "ActionCreateDTO",
    "ActionReadDTO",
    "ActionReadWithDetailsDTO",
    "ActionUpdateDTO",
    # arena
    "ArenaBaseDTO",
    "ArenaCreateDTO",
    "ArenaUpdateDTO",
    "ArenaReadDTO",
    # country
    "CountryBaseDTO",
    "CountryCreateDTO",
    "CountryUpdateDTO",
    "CountryReadDTO",
    # player
    "PlayerBaseDTO",
    "PlayerCreateDTO",
    "PlayerReadDTO",
    "PlayerUpdateDTO",
]
