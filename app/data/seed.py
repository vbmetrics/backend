import json
from pathlib import Path

from app.database import SessionLocal
from app.models import Country


print("Starting the seeding process...")

db = SessionLocal()

if db.query(Country).first():
    print("Countries table is not empty. Skipping seeding.")
else:
    print("Countries table is empty. Seeding data...")
    
    script_dir = Path(__file__).parent
    
    json_path = script_dir / 'countries.json'

    with open(json_path, 'r') as f:
        countries_data = json.load(f)

    countries_to_add = [
        Country(code=country['code'], name=country['name'])
        for country in countries_data
    ]

    try:
        db.bulk_save_objects(countries_to_add)
        db.commit()
        print(f"Successfully added {len(countries_to_add)} countries to the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

print("Seeding process finished.")
