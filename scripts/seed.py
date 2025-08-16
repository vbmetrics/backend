import csv
import logging
from datetime import date, datetime
from pathlib import Path

from sqlmodel import Session

from app.crud import arena as crud_arena
from app.crud import country as crud_country
from app.crud import player as crud_player
from app.crud import player_team_history as crud_player_team_history
from app.crud import season as crud_season
from app.crud import staff_member as crud_staff_member
from app.crud import staff_team_history as crud_staff_team_history
from app.crud import team as crud_team
from app.db.session import SessionLocal
from app.models import (
    ArenaCreate,
    CountryCreate,
    PlayerCreate,
    PlayerTeamHistoryCreate,
    SeasonCreate,
    StaffMemberCreate,
    StaffTeamHistoryCreate,
    TeamCreate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def seed_arenas(db: Session) -> None:
    arenas_csv_path = DATA_DIR / "arena.csv"
    logging.info(f"Seeding arenas from {arenas_csv_path}")

    with open(arenas_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            arena_name = row["name"]

            existing_arena = crud_arena.get_by_name(db=db, name=arena_name)
            if not existing_arena:
                arena_in = ArenaCreate(
                    name=arena_name,
                    city=row["city"],
                    address=row.get("address"),
                    capacity=int(row["capacity"]) if row.get("capacity") else None,
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

            exisiting_country = crud_country.get(db=db, id=country_code)
            if not exisiting_country:
                country_in = CountryCreate(
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

    all_teams = crud_team.get_multi(db, limit=50)
    team_lookup = {t.name: t.id for t in all_teams}

    all_seasons = crud_season.get_multi(db, limit=10)
    season_lookup = {s.name: s.id for s in all_seasons}

    with open(history_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_name, last_name = row["first_name"], row["last_name"]
            team_name, season_name = row["team_name"], row["season_name"]

            player_id = player_lookup.get((first_name, last_name))
            team_id = team_lookup.get(team_name)
            season_id = season_lookup.get(season_name)

            if not all([player_id, team_id, season_id]):
                logging.warning(
                    f"Could not find matching ID for row: "
                    f"'{last_name}', '{team_name}', '{season_name}'. Skipping..."
                )
                continue

            assert player_id is not None
            assert team_id is not None
            assert season_id is not None

            existing_history = crud_player_team_history.get_by_foreign_keys(
                db, player_id=player_id, team_id=team_id, season_id=season_id
            )

            if not existing_history:
                start_date_str = row.get("start_date")
                end_date_str = row.get("end_date")
                jersey_num_str = row.get("jersey_number")

                start_date = (
                    date.fromisoformat(start_date_str) if start_date_str else None
                )
                end_date = date.fromisoformat(end_date_str) if end_date_str else None
                jersey_number = int(jersey_num_str) if jersey_num_str else None

                history_in = PlayerTeamHistoryCreate(
                    jersey_number=jersey_number,
                    start_date=start_date,
                    end_date=end_date,
                    player_id=player_id,
                    team_id=team_id,
                    season_id=season_id,
                )
                crud_player_team_history.create(db, obj_in=history_in)
                logging.info(
                    f"Created history for: {first_name} {last_name} in {team_name}"
                )
            else:
                logging.info(
                    f"History for '{first_name} {last_name}' in '{team_name}' "
                    f"for season '{season_name}' already exists. Skipping."
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

            existing_player = crud_player.get_by_name(
                db=db, first_name=first_name, last_name=last_name
            )
            if not existing_player:
                dob_string = row.get("date_of_birth")
                dob_date = None
                if dob_string:
                    try:
                        dob_datetime = datetime.strptime(dob_string, "%d/%m/%Y")
                        dob_date = dob_datetime.date()
                    except ValueError:
                        logging.warning(
                            f"Invalid date format for {last_name}: {dob_string}"
                        )
                        continue
                player_in = PlayerCreate(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=dob_date,
                    nationality_code=row["nationality_code"],
                    height_cm=int(row["height_cm"]) if row.get("height_cm") else None,
                    weight_kg=int(row["weight_kg"]) if row.get("weight_kg") else None,
                    playing_position=row.get("playing_position") or None,
                    dominant_hand=row.get("dominant_hand") or None,
                    spike_reach_cm=int(row["spike_reach_cm"])
                    if row.get("spike_reach_cm")
                    else None,
                    block_reach_cm=int(row["block_reach_cm"])
                    if row.get("block_reach_cm")
                    else None,
                    photo_url=row.get("photo_url") or None,
                    bio=row.get("bio") or None,
                )
                crud_player.create(db=db, obj_in=player_in)
                logging.info(
                    f"Created player: {player_in.first_name} {player_in.last_name}"
                )
            else:
                logging.info(
                    f"Player {first_name} {last_name} already exists, skipping."
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
            if not existing_season:
                season_in = SeasonCreate(
                    name=season_name,
                    season_type=row["season_type"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                )
                crud_season.create(db=db, obj_in=season_in)
                logging.info(f"Created season: {season_in.name}")
            else:
                logging.info(f"Season {season_name} already exists, skipping.")


def seed_staff_members(db: Session) -> None:
    staff_members_csv_path = DATA_DIR / "staff_member.csv"
    logging.info(f"Seeding staff members from {staff_members_csv_path}.")

    with open(staff_members_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_name = row["first_name"]
            last_name = row["last_name"]

            existing_staff_member = crud_staff_member.get_by_name(
                db=db, first_name=first_name, last_name=last_name
            )
            if not existing_staff_member:
                staff_member_in = StaffMemberCreate(
                    first_name=first_name,
                    last_name=last_name,
                    role_type=row["role_type"],
                    nationality_code=row["nationality_code"],
                )
                crud_staff_member.create(db=db, obj_in=staff_member_in)
                logging.info(f"Created staff member: {staff_member_in.last_name}")
            else:
                logging.info(
                    f"Staff member {first_name} {last_name} already exists, skipping."
                )


def seed_staff_team_history(db: Session) -> None:
    history_csv_path = DATA_DIR / "staff_team_history.csv"
    logging.info(f"Seeding staff team history from {history_csv_path}")

    all_staff = crud_staff_member.get_multi(db=db, limit=50)
    staff_lookup = {(s.first_name, s.last_name): s.id for s in all_staff}

    all_teams = crud_team.get_multi(db=db, limit=50)
    team_lookup = {t.name: t.id for t in all_teams}

    all_seasons = crud_season.get_multi(db=db, limit=10)
    season_lookup = {s.name: s.id for s in all_seasons}

    with open(history_csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_name, last_name = row["first_name"], row["last_name"]
            team_name, season_name = row["team_name"], row["season_name"]

            staff_id = staff_lookup.get((first_name, last_name))
            team_id = team_lookup.get(team_name)
            season_id = season_lookup.get(season_name)

            if not all([staff_id, team_id, season_id]):
                logging.warning(
                    f"Could not find matching ID for row:"
                    f"{first_name} {last_name}, {team_name}, {season_name}. Skipping..."
                )
                continue

            assert staff_id is not None
            assert team_id is not None
            assert season_id is not None

            existing_history = crud_staff_team_history.get_by_foreign_keys(
                db=db,
                staff_member_id=staff_id,
                team_id=team_id,
                season_id=season_id,
            )

            if not existing_history:
                history_in = StaffTeamHistoryCreate(
                    role=row["role"],
                    staff_member_id=staff_id,
                    team_id=team_id,
                    season_id=season_id,
                )
                crud_staff_team_history.create(db=db, obj_in=history_in)
                logging.info(
                    f"Created history for {first_name} {last_name} "
                    "in {team_name} in season {season_name}."
                )
            else:
                logging.info(
                    f"History for {first_name} {last_name} in {team_name}"
                    "for season {season_name} already exists, skipping..."
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
            if not existing_team:
                team_in = TeamCreate(
                    name=team_name,
                    team_type=row["team_type"],
                    country_code=row["country_code"],
                    home_arena_id=row.get("home_arena_id") or None,
                    logo_url=row.get("logo_url") or None,
                    website_url=row.get("website_url") or None,
                    email=row.get("email") or None,
                )
                crud_team.create(db=db, obj_in=team_in)
                logging.info(f"Created team: {team_in.name}")
            else:
                logging.info(f"Team {team_name} already exists, skipping.")


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
    # history tables need to be seeded after teams, players, staff members and seasons
    seed_player_team_history(db)
    seed_staff_team_history(db)

    db.close()
    logging.info("Seeding process finished successfully")


if __name__ == "__main__":
    main()
