from fastapi import APIRouter

from . import (
    arena,
    country,
    player,
    player_team_history,
    season,
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
