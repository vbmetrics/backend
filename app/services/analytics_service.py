from collections import defaultdict
from typing import Optional
from uuid import UUID

from sqlalchemy import asc
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from app.models.action import Action
from app.models.match import Match
from app.models.rally import Rally
from app.models.set import Set
from app.models.special_event import SpecialEvent
from app.schemas.analytics import (
    DashboardBestPlayersDTO,
    DashboardPlayerStatDTO,
    DashboardStatsDTO,
    DashboardTeamStatsDTO,
    MatchReportDTO,
    PlayerBoxScoreDTO,
    TeamStatsDTO,
)


class MatchAnalyticsService:

    def generate_report(self, db: Session, match_id: UUID) -> MatchReportDTO:
        # 1. Pobieramy Mecz i wszystkie jego Rallies, Actions oraz Zdarzenia Specjalne
        m = db.exec(select(Match).where(Match.id == match_id)).first()
        if not m:
            raise ValueError("Match not found")

        actions = db.exec(
            select(Action)
            .join(Rally, Action.rally_id == Rally.id)
            .join(Set, Rally.set_id == Set.id)
            .where(Set.match_id == match_id)
            .options(joinedload(Action.player))
            .order_by(asc(Action.rally_id), asc(Action.sequence_in_rally))
        ).all()

        special_events = db.exec(
            select(SpecialEvent).where(SpecialEvent.match_id == match_id)
        ).all()

        # Inicjalizacja słowników na zawodników {player_id: PlayerBoxScoreDTO}
        players_stats = defaultdict(lambda: self._empty_player_stats())

        # Puste statystyki drużyn
        t_stats = {
            m.home_team_id: {"pts": 0, "atk_k": 0, "atk_tot": 0, "atk_err": 0, "blk": 0, "ace": 0, "rec_pos": 0, "rec_tot": 0, "err": 0},  # noqa: E501
            m.away_team_id: {"pts": 0, "atk_k": 0, "atk_tot": 0, "atk_err": 0, "blk": 0, "ace": 0, "rec_pos": 0, "rec_tot": 0, "err": 0}  # noqa: E501
        }

        # 2. Przetwarzanie akcji (Akcja po Akcji)
        # Aby wykryć zablokowany atak, zapamiętujemy "poprzednią" akcję w wymianie
        prev_action = None

        for action in actions:
            if not action.player_id:
                continue

            p_id = action.player_id
            team_id = m.home_team_id if action.team_context == 'H' else m.away_team_id
            skill = action.skill_code
            ev = action.evaluation_code

            # Wypełnienie bazowych danych gracza jeśli go jeszcze nie ma
            if not players_stats[p_id]["name"]:
                # Tutaj powinno być pobranie imienia i nazwiska z relacji Action.player
                if action.player:
                    players_stats[p_id]["name"] = f"{action.player.first_name} {action.player.last_name}".strip()  # noqa: E501
                    players_stats[p_id]["position"] = action.player.playing_position or "?"  # noqa: E501
                players_stats[p_id]["jersey_number"] = action.player_jersey_number
                players_stats[p_id]["player_id"] = p_id
                players_stats[p_id]["_team_id"] = team_id

            stats = players_stats[p_id]
            t = t_stats[team_id]

            # --- REGUŁY BIZNESOWE ---

            # TOTAL ERRORS (Wszystkie '-' z wyjątkiem Obrony 'D')
            if ev == '-' and skill != 'D':
                stats["total_errors"] += 1
                t["err"] += 1

            # ATAK (A)
            if skill == 'A':
                stats["attack_attempts"] += 1
                t["atk_tot"] += 1
                if ev == '#':
                    stats["attack_kills"] += 1
                    stats["points"] += 1
                    t["atk_k"] += 1
                elif ev == '-':
                    stats["attack_errors"] += 1
                    t["atk_err"] += 1

            # ROZEGRANIE (P) -> Podstawa do badania dystrybucji ataku w przyszłości
            if skill == 'P':
                stats["pass_attempts"] += 1

            # BLOK (B)
            if skill == 'B':
                if ev == '#':
                    stats["block_kills"] += 1
                    stats["points"] += 1
                    t["blk"] += 1
                    # Sprawdzenie zablokowanego ataku rywala
                    if prev_action and prev_action.skill_code == 'A' and prev_action.team_context != action.team_context:  # noqa: E501
                        players_stats[prev_action.player_id]["attack_blocked"] += 1
                elif ev == '+':
                    stats["block_touches"] += 1
                elif ev == '-':
                    stats["block_errors"] += 1

            # ZAGRYWKA (S)
            if skill == 'S':
                stats["serve_attempts"] += 1
                if ev == '#':
                    stats["serve_aces"] += 1
                    stats["points"] += 1
                    t["ace"] += 1
                elif ev == '-':
                    stats["serve_errors"] += 1

            # PRZYJĘCIE (R)
            if skill == 'R':
                stats["reception_attempts"] += 1
                t["rec_tot"] += 1
                if ev == '#':
                    stats["reception_perfect"] += 1
                    t["rec_pos"] += 1
                elif ev == '+':
                    stats["reception_positive"] += 1
                    t["rec_pos"] += 1
                elif ev == '-':
                    stats["reception_errors"] += 1

            # OBRONA (D)
            if skill == 'D':
                if ev == '+':
                    stats["dig_success"] += 1
                elif ev == '-':
                    stats["dig_errors"] += 1

            prev_action = action

        # 3. Przetwarzanie Błędów Specjalnych (Kary, Ustawienie) z parsera
        for evt in special_events:
            # Zakładamy, że karny punkt !F- lub !RC ląduje w bazie
            if evt.raw_special_code.startswith("!F-") or evt.raw_special_code.startswith("!RC"):  # noqa: E501
                # Karę (błąd) zapisujemy drużynie, która ją otrzymała
                t_stats[evt.team_id]["err"] += 1

        # 4. Finalne przeliczenia (% i wydajność)
        final_home_box = []
        final_away_box = []

        for p_id, s in players_stats.items():
            if not s["name"]:
                continue # Puste rekordy

            # Atak
            if s["attack_attempts"] > 0:
                s["attack_accuracy"] = round(
                    (s["attack_kills"] / s["attack_attempts"]) * 100, 1
                )
                # Eff = (A# - A-) / Tot
                s["attack_efficiency"] = round(
                    (
                        (s["attack_kills"] - s["attack_errors"]) / s["attack_attempts"]
                    ) * 100,
                    1
                )

            # Przyjęcie
            if s["reception_attempts"] > 0:
                s["reception_perf_pct"] = round(
                    (s["reception_perfect"] / s["reception_attempts"]) * 100, 1
                )
                s["reception_pos_pct"] = round(
                    (
                        (s["reception_perfect"] + s["reception_positive"]) / s["reception_attempts"]  # noqa: E501
                    ) * 100,
                    1
                )

            # Zagrywka (Twój wskaźnik opłacalności ryzyka)
            if s["serve_attempts"] > 0:
                s["serve_yield"] = round(
                    (s["serve_aces"] - s["serve_errors"]) / s["serve_attempts"], 2
                )

            dto = PlayerBoxScoreDTO(**s)

            # Przypisanie do dobrej tablicy - sprawdzamy historię żeby ustalić team,
            # (W uproszczeniu: jeśli jego id pojawia się w zapytaniach drużyny A)
            # Najlepiej odczytać to po prostu ze statystyk
            # (zakładamy że gracz całe spotkanie gra w 1 drużynie)
            if s.get("_team_id") == m.home_team_id:
                final_home_box.append(dto)
            else:
                final_away_box.append(dto)

        # Przeliczenie Team Stats
        def build_team_stats(team_id):
            ts = t_stats[team_id]
            atk_eff = round(
                ((ts["atk_k"] - ts["atk_err"]) / ts["atk_tot"] * 100), 1
            ) if ts["atk_tot"] > 0 else 0.0
            rec_pos = round(
                (ts["rec_pos"] / ts["rec_tot"] * 100), 1
            ) if ts["rec_tot"] > 0 else 0.0
            return TeamStatsDTO(
                attack_eff=atk_eff,
                kill_blocks=ts["blk"],
                aces=ts["ace"],
                reception_pos=rec_pos,
                total_errors=ts["err"]
            )

        return MatchReportDTO(
            match_id=match_id,
            home_team_stats=build_team_stats(m.home_team_id),
            away_team_stats=build_team_stats(m.away_team_id),
            home_box_score=final_home_box,
            away_box_score=final_away_box
        )

    def _empty_player_stats(self):
        return {
            "player_id": None, "name": "", "jersey_number": 0, "position": "", "points": 0,  # noqa: E501
            "attack_attempts": 0, "attack_kills": 0, "attack_errors": 0, "attack_blocked": 0, "attack_accuracy": 0.0, "attack_efficiency": 0.0,  # noqa: E501
            "reception_attempts": 0, "reception_perfect": 0, "reception_positive": 0, "reception_errors": 0, "reception_perf_pct": 0.0, "reception_pos_pct": 0.0,  # noqa: E501
            "serve_attempts": 0, "serve_aces": 0, "serve_errors": 0, "serve_yield": 0.0,
            "block_kills": 0, "block_touches": 0, "block_errors": 0,
            "dig_success": 0, "dig_errors": 0, "pass_attempts": 0,
            "total_errors": 0, "_team_id": None
        }

    def generate_dashboard_stats(self, db: Session, team_id: UUID, season_id: Optional[UUID] = None) -> DashboardStatsDTO:  # noqa: E501
        # 1. Znajdź mecze tej drużyny
        query = select(Match).where((Match.home_team_id == team_id) | (Match.away_team_id == team_id))  # noqa: E501
        if season_id:
            query = query.where(Match.season_id == season_id)

        matches = db.exec(query).all()
        match_ids = [m.id for m in matches]

        if not match_ids:
            # Zwracamy puste dane, jeśli drużyna nie ma meczów
            return DashboardStatsDTO(
                team_stats=DashboardTeamStatsDTO(sideout_pct=0.0, breakpoint_pct=0.0),
                best_players=DashboardBestPlayersDTO()
            )

        # 2. Pobierzmy Rallies (Wymiany) i Actions (Akcje) dla tych meczów
        rallies = db.exec(select(Rally).where(Rally.match_id.in_(match_ids))).all()
        actions = db.exec(
            select(Action)
            .where(Action.match_id.in_(match_ids))
            .options(joinedload(Action.player))
        ).all()

        # --- OBLICZANIE WSKAŹNIKÓW DRUŻYNOWYCH ---
        total_serve_receive_attempts = 0
        rallies_won_on_reception = 0

        total_service_attempts = 0
        break_points_won = 0

        for r in rallies:
            # Kto wygrał tę wymianę? (Mamy to zdefiniowane w r.score_team_id)
            rally_winner = r.score_team_id

            if r.serve_team_id == team_id:
                # My zagrywamy -> Faza Break Point
                total_service_attempts += 1
                if rally_winner == team_id:
                    break_points_won += 1
            elif r.serve_team_id is not None and r.serve_team_id != team_id:
                # Przeciwnik zagrywa -> Faza Side-Out (Przyjęcie)
                total_serve_receive_attempts += 1
                if rally_winner == team_id:
                    rallies_won_on_reception += 1

        sideout_pct = round((rallies_won_on_reception / total_serve_receive_attempts * 100), 1) if total_serve_receive_attempts > 0 else 0.0  # noqa: E501
        breakpoint_pct = round((break_points_won / total_service_attempts * 100), 1) if total_service_attempts > 0 else 0.0  # noqa: E501

        # --- WYSZUKIWANIE LIDERÓW ---
        players_data = defaultdict(
            lambda: {"name": "", "pts": 0, "blks": 0, "aces": 0, "perf_rec": 0}
        )

        for a in actions:
            # Interesują nas tylko akcje zawodników naszego zespołu
            # Trzeba sprawdzić czy dany zawodnik należy do team_id
            m = next((x for x in matches if x.id == a.match_id), None)
            if not m:
                continue

            is_our_action = (m.home_team_id == team_id and a.team_context == 'H') or \
                            (m.away_team_id == team_id and a.team_context == 'G')

            if not is_our_action or not a.player_id:
                continue

            pid = a.player_id
            if not players_data[pid]["name"] and a.player:
                players_data[pid]["name"] = f"{a.player.first_name[0]}. {a.player.last_name}" if a.player.first_name else a.player.last_name  # noqa: E501

            skill = a.skill_code
            ev = a.evaluation_code

            if skill == 'A' and ev == '#':
                players_data[pid]["pts"] += 1
            if skill == 'B' and ev == '#':
                players_data[pid]["pts"] += 1
                players_data[pid]["blks"] += 1
            if skill == 'S' and ev == '#':
                players_data[pid]["pts"] += 1
                players_data[pid]["aces"] += 1
            if skill == 'R' and ev == '#':
                players_data[pid]["perf_rec"] += 1

        # Wyłonienie liderów
        best_scorer = max(players_data.values(), key=lambda x: x["pts"], default=None)
        best_blocker = max(players_data.values(), key=lambda x: x["blks"], default=None)
        best_server = max(players_data.values(), key=lambda x: x["aces"], default=None)
        best_receiver = max(players_data.values(), key=lambda x: x["perf_rec"], default=None)  # noqa: E501

        def map_leader(player, stat_key):
            if player and player[stat_key] > 0:
                return DashboardPlayerStatDTO(
                    name=player["name"], value=player[stat_key]
                )
            return None

        return DashboardStatsDTO(
            team_stats=DashboardTeamStatsDTO(
                sideout_pct=sideout_pct,
                breakpoint_pct=breakpoint_pct
            ),
            best_players=DashboardBestPlayersDTO(
                scorer=map_leader(best_scorer, "pts"),
                blocker=map_leader(best_blocker, "blks"),
                server=map_leader(best_server, "aces"),
                receiver=map_leader(best_receiver, "perf_rec")
            )
        )
