import csv
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from pydantic import HttpUrl, TypeAdapter
from sqlmodel import Session

# CRUD instances – zakładam, że masz je eksportowane w app.crud.__init__
from app.crud import arena as crud_arena
from app.crud import country as crud_country
from app.crud import player as crud_player
from app.crud import player_team_history as crud_player_team_history
from app.crud import season as crud_season
from app.crud import staff_member as crud_staff_member
from app.crud import staff_team_history as crud_staff_team_history
from app.crud import team as crud_team
from app.db.session import SessionLocal

# Enumy z modeli (źródło prawdy wartości)
from app.models.player import PlayerHand, PlayerPosition
from app.models.season import SeasonType
from app.models.staff_member import StaffRoleType
from app.models.team import TeamType

# DTOs (schemas), nie modele ORM
from app.schemas import (
    ArenaCreateDTO,
    CountryCreateDTO,
    PlayerCreateDTO,
    PlayerTeamHistoryCreateDTO,
    SeasonCreateDTO,
    StaffMemberCreateDTO,
    StaffTeamHistoryCreateDTO,
    TeamCreateDTO,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
_URL_ADAPTER = TypeAdapter(HttpUrl)


def _parse_http_url(value: Optional[str]) -> Optional[HttpUrl]:
    if not value:
        return None
    try:
        # zaakceptuj też " " lub puste po trimie
        val = value.strip()
        if not val:
            return None
        return _URL_ADAPTER.validate_python(val)
    except Exception:
        return None


def _parse_optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_ddmmyyyy(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError:
        return None


def seed_arenas(db: Session) -> None:
    arenas_csv_path = DATA_DIR / "arena.csv"
    logging.info(f"Seeding arenas from {arenas_csv_path}")

    with open(arenas_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            arena_name = row["name"]

            existing_arena = crud_arena.get_by_name(db=db, name=arena_name)
            if not existing_arena:
                arena_in = ArenaCreateDTO(
                    name=arena_name,
                    city=row.get("city") or None,
                    address=row.get("address") or None,
                    capacity=_parse_optional_int(row.get("capacity")),
                    country_code=row["country_code"],
                )
                crud_arena.create(db=db, obj_in=arena_in)
                logging.info(f"Created arena: {arena_in.name}")
            else:
                logging.info(f"Arena {arena_name} already exists, skipping.")

    logging.info("Finished seeding arenas.")


def seed_countries(db: Session) -> None:
    countries_csv_path = DATA_DIR / "country.csv"
    logging.info(f"Seeding countries from {countries_csv_path}")

    with open(countries_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            country_code = row["alpha_2_code"]

            existing_country = crud_country.get(db, country_code)  # type: ignore[misc]
            if not existing_country:
                country_in = CountryCreateDTO(
                    name=row["name"],
                    alpha_2_code=country_code,
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                )
                crud_country.create(db=db, obj_in=country_in)
                logging.info(f"Created country: {country_in.name}")
            else:
                logging.info(f"Country {country_code} already exists, skipping.")

    logging.info("Finished seeding countries.")


def seed_player_team_history(db: Session) -> None:
    history_csv_path = DATA_DIR / "player_team_history.csv"
    logging.info(f"Seeding player team history from {history_csv_path}")

    all_players = crud_player.get_multi(db, limit=500)
    player_lookup = {(p.first_name, p.last_name): p.id for p in all_players}

    all_teams = crud_team.get_multi(db, limit=200)
    team_lookup = {t.name: t.id for t in all_teams}

    all_seasons = crud_season.get_multi(db, limit=100)
    season_lookup = {s.name: s.id for s in all_seasons}

    with open(history_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_name, last_name = row["first_name"], row["last_name"]
            team_name, season_name = row["team_name"], row["season_name"]

            player_id = player_lookup.get((first_name, last_name))
            team_id = team_lookup.get(team_name)
            season_id = season_lookup.get(season_name)

            if not (player_id and team_id and season_id):
                logging.warning(
                    f"Could not find matching ID for row: "
                    f"{first_name} {last_name}, {team_name}, {season_name}. Skipping..."
                )
                continue

            existing_histories = crud_player_team_history.get_multi(
                db,
                limit=1,
                player_id=player_id,
                team_id=team_id,
                season_id=season_id,
            )
            if not existing_histories:
                start_date = _parse_iso_date(row.get("start_date"))
                end_date = _parse_iso_date(row.get("end_date"))
                jersey_number = _parse_optional_int(row.get("jersey_number"))

                history_in = PlayerTeamHistoryCreateDTO(
                    jersey_number=jersey_number,
                    start_date=start_date or date.today(),
                    end_date=end_date,
                    player_id=player_id,
                    team_id=team_id,
                    season_id=season_id,
                )
                crud_player_team_history.create(db, obj_in=history_in)
                logging.info(
                    f"Created {first_name} {last_name} in {team_name} ({season_name})"
                )
            else:
                logging.info(
                    f"History for {first_name} {last_name} in {team_name} "
                    f"for season {season_name} already exists. Skipping."
                )

    logging.info("Seeding player team history finished.")


def seed_players(db: Session) -> None:
    players_csv_path = DATA_DIR / "player.csv"
    logging.info(f"Seeding players from {players_csv_path}")

    with open(players_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            first_name = row["first_name"]
            last_name = row["last_name"]

            existing = [
                p
                for p in crud_player.get_multi(db=db, limit=50, search=last_name)
                if p.first_name == first_name and p.last_name == last_name
            ]
            if existing:
                logging.info(
                    f"Player {first_name} {last_name} already exists, skipping."
                )
                continue

            dob_date = _parse_ddmmyyyy(row.get("date_of_birth"))
            if dob_date is None:
                logging.warning(
                    f"Invalid or missing date_of_birth for {first_name} {last_name}"
                )
                continue

            # Enumy są opcjonalne – mapujemy tylko gdy podano wartość
            playing_position = row.get("playing_position") or None
            dominant_hand = row.get("dominant_hand") or None

            try:
                position_val = (
                    PlayerPosition(playing_position) if playing_position else None
                )
            except ValueError:
                logging.warning(
                    f"Unknown position '{playing_position}' - {first_name} {last_name}"
                )  # noqa
                position_val = None

            try:
                hand_val = PlayerHand(dominant_hand) if dominant_hand else None
            except ValueError:
                logging.warning(
                    f"Unknown hand '{dominant_hand}' for {first_name} {last_name}"
                )  # noqa
                hand_val = None

            player_in = PlayerCreateDTO(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob_date,
                nationality_code=row["nationality_code"],
                height_cm=_parse_optional_int(row.get("height_cm")),
                weight_kg=_parse_optional_int(row.get("weight_kg")),
                playing_position=position_val,
                dominant_hand=hand_val,
                spike_reach_cm=_parse_optional_int(row.get("spike_reach_cm")),
                block_reach_cm=_parse_optional_int(row.get("block_reach_cm")),
                photo_url=row.get("photo_url") or None,
                bio=row.get("bio") or None,
            )
            crud_player.create(db=db, obj_in=player_in)
            logging.info(
                f"Created player: {player_in.first_name} {player_in.last_name}"
            )

    logging.info("Finished seeding players.")


def seed_seasons(db: Session) -> None:
    seasons_csv_path = DATA_DIR / "season.csv"
    logging.info(f"Seeding seasons from {seasons_csv_path}")

    with open(seasons_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            season_name = row["name"]

            existing_season = crud_season.get_by_name(db=db, name=season_name)
            if existing_season:
                logging.info(f"Season {season_name} already exists, skipping.")
                continue

            # Mapowanie enumu + dat
            try:
                stype = SeasonType(row["season_type"])
            except ValueError:
                logging.warning(
                    f"Unknown season_type '{row['season_type']}' for {season_name}"
                )  # noqa
                continue

            start_date = _parse_iso_date(row.get("start_date"))
            end_date = _parse_iso_date(row.get("end_date"))
            if not start_date or not end_date or end_date < start_date:
                logging.warning(f"Invalid dates for season {season_name}; skipping.")
                continue

            season_in = SeasonCreateDTO(
                name=season_name,
                season_type=stype,
                start_date=start_date,
                end_date=end_date,
            )
            crud_season.create(db=db, obj_in=season_in)
            logging.info(f"Created season: {season_in.name}")


def seed_staff_members(db: Session) -> None:
    staff_members_csv_path = DATA_DIR / "staff_member.csv"
    logging.info(f"Seeding staff members from {staff_members_csv_path}.")

    with open(staff_members_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_name = row["first_name"]
            last_name = row["last_name"]

            # Brak get_by_name -> szukamy w get_multi(search=...)
            existing = [
                s
                for s in crud_staff_member.get_multi(db=db, limit=50, search=last_name)
                if s.first_name == first_name and s.last_name == last_name
            ]
            if existing:
                logging.info(
                    f"Staff member {first_name} {last_name} already exists, skipping."
                )
                continue

            try:
                role = StaffRoleType(row["role_type"])
            except ValueError:
                logging.warning(
                    f"Unknown srole '{row['role_type']}' for {first_name} {last_name}"
                )  # noqa
                continue

            staff_member_in = StaffMemberCreateDTO(
                first_name=first_name,
                last_name=last_name,
                role_type=role,
                nationality_code=row["nationality_code"],
            )
            crud_staff_member.create(db=db, obj_in=staff_member_in)
            logging.info(f"Created staff member: {first_name} {last_name}")


def seed_staff_team_history(db: Session) -> None:
    history_csv_path = DATA_DIR / "staff_team_history.csv"
    logging.info(f"Seeding staff team history from {history_csv_path}")

    all_staff = crud_staff_member.get_multi(db=db, limit=500)
    staff_lookup = {(s.first_name, s.last_name): s.id for s in all_staff}

    all_teams = crud_team.get_multi(db=db, limit=200)
    team_lookup = {t.name: t.id for t in all_teams}

    all_seasons = crud_season.get_multi(db=db, limit=200)
    season_lookup = {s.name: s.id for s in all_seasons}

    with open(history_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_name, last_name = row["first_name"], row["last_name"]
            team_name, season_name = row["team_name"], row["season_name"]

            staff_id = staff_lookup.get((first_name, last_name))
            team_id = team_lookup.get(team_name)
            season_id = season_lookup.get(season_name)

            if not (staff_id and team_id and season_id):
                logging.warning(
                    f"Could not find matching ID for row: "
                    f"{first_name} {last_name}, {team_name}, {season_name}. Skipping..."
                )
                continue

            existing = crud_staff_team_history.get_multi(
                db=db,
                limit=1,
                staff_member_id=staff_id,
                team_id=team_id,
                season_id=season_id,
            )
            if not existing:
                history_in = StaffTeamHistoryCreateDTO(
                    role=row["role"],
                    staff_member_id=staff_id,
                    team_id=team_id,
                    season_id=season_id,
                )
                crud_staff_team_history.create(db=db, obj_in=history_in)
                logging.info(
                    f"Created {first_name} {last_name} in {team_name} ({season_name})."
                )
            else:
                logging.info(
                    f"History for {first_name} {last_name} in {team_name} "
                    f"for season {season_name} already exists, skipping..."
                )

    logging.info("Finished seeding staff team history.")


def seed_teams(db: Session) -> None:
    teams_csv_path = DATA_DIR / "team.csv"
    logging.info(f"Seeding teams from {teams_csv_path}")

    with open(teams_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            team_name = row["name"]

            existing_team = crud_team.get_by_name(db=db, name=team_name)
            if existing_team:
                logging.info(f"Team {team_name} already exists, skipping.")
                continue

            # Enum TeamType
            try:
                ttype = TeamType(row["team_type"])
            except ValueError:
                logging.warning(
                    f"Unknown team_type '{row['team_type']}' for {team_name}; skipping."
                )
                continue

            home_arena_id_str = row.get("home_arena_id") or None
            home_arena_id: Optional[UUID] = None
            if home_arena_id_str:
                try:
                    home_arena_id = UUID(home_arena_id_str)
                except ValueError:
                    logging.warning(
                        f"Invalid home_arena_id '{home_arena_id_str}' for {team_name}"
                    )  # noqa
                    home_arena_id = None

            team_in = TeamCreateDTO(
                name=team_name,
                team_type=ttype,
                country_code=row["country_code"],
                home_arena_id=home_arena_id,
                logo_url=_parse_http_url(row.get("logo_url")),
                website_url=_parse_http_url(row.get("website_url")),
                email=(row.get("email") or None),
            )
            crud_team.create(db=db, obj_in=team_in)
            logging.info(f"Created team: {team_in.name}")


def seed_matches(db: Session) -> None:
    # TODO: prepare match data and load it to database
    pass


def main() -> None:
    logging.info("Starting the seeding process")
    db = SessionLocal()

    # start with countries
    seed_countries(db)
    # then other entities that depend on countries
    seed_arenas(db)
    seed_players(db)
    seed_seasons(db)
    seed_staff_members(db)
    seed_teams(db)
    seed_matches(db)
    # history tables need to be seeded after teams, players, staff members and seasons
    seed_player_team_history(db)
    seed_staff_team_history(db)

    db.close()
    logging.info("Seeding process finished successfully")


if __name__ == "__main__":
    main()
