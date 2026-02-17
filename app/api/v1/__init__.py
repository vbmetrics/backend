from fastapi import APIRouter

from . import (
    action,
    arena,
    auth,
    country,
    lineup,
    live,
    match,
    match_flow,
    player,
    player_team_history,
    rally,
    season,
    set,
    special_event,
    staff_member,
    staff_team_history,
    team,
)

api_router = APIRouter()

api_router.include_router(arena.router)
api_router.include_router(country.router)
api_router.include_router(player.router)
api_router.include_router(player_team_history.router)
api_router.include_router(season.router)
api_router.include_router(staff_member.router)
api_router.include_router(staff_team_history.router)
api_router.include_router(team.router)
api_router.include_router(auth.router)
api_router.include_router(match.router)
api_router.include_router(set.router)
api_router.include_router(rally.router)
api_router.include_router(action.router)
api_router.include_router(special_event.router)
api_router.include_router(match_flow.router)
api_router.include_router(live.router)
api_router.include_router(lineup.router)
