import time

from faker import Faker
from sqlalchemy import insert
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Building, Company, Desk, Floor, Location

fake = Faker("en_US")

COMPANIES_COUNT = 100
BUILDINGS_PER_COMPANY = 100
FLOORS_PER_BUILDING = 3
DESKS_PER_FLOOR = 100
BATCH_SIZE = 100000

DESK_STATUSES = ("available", "occupied", "maintenance")
DESK_EQUIPMENT = (
    "monitor, ergonomic chair",
    "monitor, ergonomic chair, docking station",
    "dual monitor, ergonomic chair",
    "monitor, standing desk",
)


def bulk_insert_ids(session: Session, table, rows):
    if not rows:
        return []

    statement = insert(table).returning(table.id)
    return session.execute(statement, rows).scalars().all()


def flush_desks(session: Session, desks_batch, desks_inserted, total_desks):
    if not desks_batch:
        return desks_inserted

    session.execute(insert(Desk), desks_batch)
    session.commit()

    desks_inserted += len(desks_batch)
    print(f"Inserted {desks_inserted} / {total_desks} desks...")
    desks_batch.clear()
    return desks_inserted


def clear_seed_data(session: Session):
    session.execute(
        text(
            "TRUNCATE TABLE reservation, desk, floor, work_group_building, work_group, employee, building, location, user_group, company RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


def seed_database():
    start_time = time.time()

    with SessionLocal() as session:
        print("Clearing previously generated data...")
        clear_seed_data(session)

        print(f"Generating {COMPANIES_COUNT} companies...")
        companies_data = []
        for company_number in range(1, COMPANIES_COUNT + 1):
            company_name = fake.company()[:80]
            companies_data.append(
                {
                    "name": f"Company {company_number:03d} - {company_name}",
                    "group_name": f"Group {((company_number - 1) % 10) + 1:02d}",
                }
            )

        company_ids = bulk_insert_ids(session, Company, companies_data)
        session.commit()

        total_buildings = len(company_ids) * BUILDINGS_PER_COMPANY
        print(f"Generating {total_buildings} buildings and locations...")

        locations_data = [
            {
                "country": fake.country()[:50],
                "city": fake.city()[:100],
            }
            for _ in range(total_buildings)
        ]
        location_ids = bulk_insert_ids(session, Location, locations_data)

        buildings_data = []
        for company_index, company_id in enumerate(company_ids, start=1):
            for building_number in range(1, BUILDINGS_PER_COMPANY + 1):
                location_index = (company_index - 1) * BUILDINGS_PER_COMPANY + (building_number - 1)
                buildings_data.append(
                    {
                        "name": f"Building {company_index:03d}-{building_number:03d}",
                        "address": fake.street_address()[:100],
                        "location_id": location_ids[location_index],
                        "company_id": company_id,
                    }
                )

        building_ids = bulk_insert_ids(session, Building, buildings_data)
        session.commit()

        total_floors = len(building_ids) * FLOORS_PER_BUILDING
        print(f"Generating {total_floors} floors...")

        floors_data = []
        for building_id in building_ids:
            for level in range(1, FLOORS_PER_BUILDING + 1):
                floors_data.append(
                    {
                        "building_id": building_id,
                        "level": level,
                        "name": f"Floor {level}",
                    }
                )

        floor_ids = bulk_insert_ids(session, Floor, floors_data)
        session.commit()

        total_desks = len(floor_ids) * DESKS_PER_FLOOR
        print(f"Generating {total_desks} desks (this might take a while)...")

        desks_batch = []
        desks_inserted = 0

        for floor_index, floor_id in enumerate(floor_ids, start=1):
            floor_level = ((floor_index - 1) % FLOORS_PER_BUILDING) + 1

            for desk_number in range(1, DESKS_PER_FLOOR + 1):
                desks_batch.append(
                    {
                        "floor_id": floor_id,
                        "label": f"F{floor_level:02d}-D{desk_number:03d}",
                        "status": DESK_STATUSES[(desk_number + floor_level) % len(DESK_STATUSES)],
                        "equipment": DESK_EQUIPMENT[(desk_number + floor_index) % len(DESK_EQUIPMENT)],
                    }
                )

                if len(desks_batch) >= BATCH_SIZE:
                    desks_inserted = flush_desks(session, desks_batch, desks_inserted, total_desks)

        desks_inserted = flush_desks(session, desks_batch, desks_inserted, total_desks)

        end_time = time.time()
        print(f"\nFinished successfully! Duration: {round(end_time - start_time, 2)} seconds.")

if __name__ == "__main__":
    seed_database()