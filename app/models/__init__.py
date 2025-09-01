from .arena import (
    Arena,
    ArenaBase,
    ArenaCreate,
    ArenaRead,
    ArenaReadWithCountry,
    ArenaUpdate,
)
from .country import Country, CountryBase, CountryCreate, CountryRead, CountryUpdate
from .match import (
    Match,
    MatchBase,
    MatchCreate,
    MatchRead,
    MatchReadWithDetails,
    MatchUpdate,
)
from .player import (
    Player,
    PlayerBase,
    PlayerCreate,
    PlayerHand,
    PlayerPosition,
    PlayerRead,
    PlayerUpdate,
)
from .player_team_history import (
    PlayerTeamHistory,
    PlayerTeamHistoryBase,
    PlayerTeamHistoryCreate,
    PlayerTeamHistoryRead,
    PlayerTeamHistoryReadWithDetails,
    PlayerTeamHistoryUpdate,
)
from .rally import (
    Rally,
    RallyBase,
    RallyCreate,
    RallyRead,
    RallyReadWithDetails,
    RallyUpdate,
)
from .season import (
    Season,
    SeasonBase,
    SeasonCreate,
    SeasonRead,
    SeasonType,
    SeasonUpdate,
)
from .set import (
    Set,
    SetBase,
    SetCreate,
    SetRead,
    SetReadWithDetails,
    SetUpdate,
)
from .staff_member import (
    StaffMember,
    StaffMemberBase,
    StaffMemberCreate,
    StaffMemberRead,
    StaffMemberUpdate,
    StaffRoleType,
)
from .staff_team_history import (
    StaffTeamHistory,
    StaffTeamHistoryBase,
    StaffTeamHistoryCreate,
    StaffTeamHistoryRead,
    StaffTeamHistoryReadWithDetails,
    StaffTeamHistoryUpdate,
)
from .team import (
    Team,
    TeamBase,
    TeamCreate,
    TeamRead,
    TeamType,
    TeamUpdate,
)
from .token import Token, TokenData
from .user import (
    User,
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
)

__all__ = [
    # Arena
    "Arena",
    "ArenaBase",
    "ArenaCreate",
    "ArenaRead",
    "ArenaReadWithCountry",
    "ArenaUpdate",
    # Country
    "Country",
    "CountryBase",
    "CountryCreate",
    "CountryRead",
    "CountryUpdate",
    # Match
    "Match",
    "MatchBase",
    "MatchCreate",
    "MatchRead",
    "MatchReadWithDetails",
    "MatchUpdate",
    # Player
    "Player",
    "PlayerBase",
    "PlayerCreate",
    "PlayerRead",
    "PlayerUpdate",
    "PlayerPosition",
    "PlayerHand",
    # Rally
    "Rally",
    "RallyBase",
    "RallyCreate",
    "RallyRead",
    "RallyReadWithDetails",
    "RallyUpdate",
    # Season
    "Season",
    "SeasonBase",
    "SeasonCreate",
    "SeasonRead",
    "SeasonUpdate",
    "SeasonType",
    # Set
    "Set",
    "SetBase",
    "SetCreate",
    "SetRead",
    "SetReadWithDetails",
    "SetUpdate",
    # StaffMember
    "StaffMember",
    "StaffMemberBase",
    "StaffMemberCreate",
    "StaffMemberRead",
    "StaffMemberUpdate",
    "StaffRoleType",
    # Team
    "Team",
    "TeamBase",
    "TeamCreate",
    "TeamRead",
    "TeamUpdate",
    "TeamType",
    # PlayerTeamHistory
    "PlayerTeamHistory",
    "PlayerTeamHistoryBase",
    "PlayerTeamHistoryCreate",
    "PlayerTeamHistoryRead",
    "PlayerTeamHistoryReadWithDetails",
    "PlayerTeamHistoryUpdate",
    # StaffTeamHistory
    "StaffTeamHistory",
    "StaffTeamHistoryBase",
    "StaffTeamHistoryCreate",
    "StaffTeamHistoryRead",
    "StaffTeamHistoryReadWithDetails",
    "StaffTeamHistoryUpdate",
    # Token
    "Token",
    "TokenData",
    # User
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "User",
]

ArenaReadWithCountry.model_rebuild()
MatchReadWithDetails.model_rebuild()
RallyReadWithDetails.model_rebuild()
SetReadWithDetails.model_rebuild()
StaffTeamHistoryReadWithDetails.model_rebuild()
