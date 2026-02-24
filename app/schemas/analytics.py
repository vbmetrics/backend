from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PlayerBoxScoreDTO(BaseModel):
    player_id: UUID
    jersey_number: int
    name: str
    position: str
    points: int = 0

    # 1. Attack (A)
    attack_attempts: int = 0
    attack_kills: int = 0      # A#
    attack_errors: int = 0     # A- (w tym zablokowane)
    attack_blocked: int = 0    # Zablokowane ataki (wyciągnięte z B# przeciwnika)
    attack_accuracy: float = 0.0  # Kills / Attempts
    attack_efficiency: float = 0.0 # (Kills - Errors) / Attempts

    # 2. Reception (R)
    reception_attempts: int = 0
    reception_perfect: int = 0 # R#
    reception_positive: int = 0 # R+
    reception_errors: int = 0  # R-
    reception_perf_pct: float = 0.0 # R# / Attempts
    reception_pos_pct: float = 0.0  # (R# + R+) / Attempts

    # 3. Serve (S)
    serve_attempts: int = 0
    serve_aces: int = 0        # S#
    serve_errors: int = 0      # S-
    serve_yield: float = 0.0   # (Aces - Errors) / Attempts (ile pkt na 1 zagrywkę)

    # 4. Block (B)
    block_kills: int = 0       # B#
    block_touches: int = 0     # B+ (wybloki)
    block_errors: int = 0      # B-

    # 5. Dig (D) & Pass (P)
    dig_success: int = 0       # D+
    dig_errors: int = 0        # D- (nie wlicza się do Total Errors)
    pass_attempts: int = 0     # P (wystawy)

    # 6. Ogólne
    total_errors: int = 0      # Wszystkie błędy poza D-

class TeamStatsDTO(BaseModel):
    points: int = 0
    sets_won: int = 0

    # Sumaryczne statystyki drużyny
    attack_kills: int = 0
    attack_eff: float = 0.0
    kill_blocks: int = 0
    aces: int = 0
    reception_pos: float = 0.0
    total_errors: int = 0 # Wliczając kary i ustawienia

class MatchReportDTO(BaseModel):
    match_id: UUID
    home_team_stats: TeamStatsDTO
    away_team_stats: TeamStatsDTO
    home_box_score: list[PlayerBoxScoreDTO]
    away_box_score: list[PlayerBoxScoreDTO]

class DashboardPlayerStatDTO(BaseModel):
    name: str
    value: float

class DashboardTeamStatsDTO(BaseModel):
    sideout_pct: float
    breakpoint_pct: float

class DashboardBestPlayersDTO(BaseModel):
    scorer: Optional[DashboardPlayerStatDTO] = None
    blocker: Optional[DashboardPlayerStatDTO] = None
    server: Optional[DashboardPlayerStatDTO] = None
    receiver: Optional[DashboardPlayerStatDTO] = None

class DashboardStatsDTO(BaseModel):
    team_stats: DashboardTeamStatsDTO
    best_players: DashboardBestPlayersDTO
