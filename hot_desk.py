import os

from sqlalchemy import (
    create_engine, MetaData, Table, Column, 
    Integer, String, ForeignKey, Date, Time, DateTime, func
)
import psycopg2
from psycopg2 import Error

# # 1. Configuring the connection to the PostgreSQL database
# # Format: postgresql+psycopg2://user:password@host:port/database_name
# DATABASE_URL = "postgresql+psycopg2://user:user@localhost:5432/best_base"
# engine = create_engine(DATABASE_URL, echo=True) # echo=True will show the generated SQL code in the console

# # MetaData is a "container" for the definitions of all our tables
# metadata = MetaData()
##Not used beacues we are using raw SQL to create tables, but it can be useful for future reference when we want to use SQLAlchemy's ORM features.

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS Companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    group_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Locations (
    id SERIAL PRIMARY KEY,
    country VARCHAR(50),
    city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS UserGroups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS Buildings (
    id SERIAL PRIMARY KEY,
    location_id INT REFERENCES Locations(id) ON DELETE CASCADE,
    name VARCHAR(100),
    address VARCHAR(100),
    company_id INT REFERENCES Companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS WorkGroups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    company_id INT REFERENCES Companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Floors (
    id SERIAL PRIMARY KEY,
    building_id INT REFERENCES Buildings(id) ON DELETE CASCADE,
    level INT,
    svg_path VARCHAR(255),
    width INT,
    height INT
);

CREATE TABLE IF NOT EXISTS WorkGroup_Buildings (
    workgroup_id INT REFERENCES WorkGroups(id) ON DELETE CASCADE,
    building_id INT REFERENCES Buildings(id) ON DELETE CASCADE,
    PRIMARY KEY (workgroup_id, building_id)
);

CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    user_group_id INT REFERENCES UserGroups(id) ON DELETE SET NULL,
    workgroup_id INT REFERENCES WorkGroups(id) ON DELETE SET NULL,
    email VARCHAR(50) UNIQUE,
    hash_password VARCHAR(256)
);


CREATE TABLE IF NOT EXISTS Desks (
    id SERIAL PRIMARY KEY,
    floor_id INT REFERENCES Floors(id) ON DELETE CASCADE,
    label VARCHAR(20),
    x INT,
    y INT,
    status VARCHAR(20)
);


CREATE TABLE IF NOT EXISTS Reservations (
    id SERIAL PRIMARY KEY,
    desk_id INT REFERENCES Desks(id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(id) ON DELETE CASCADE,
    date DATE,
    start_time TIME,
    end_time TIME,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_database_schema():
    try:
        # Connecting to the PostgreSQL database from Docker
        connection = psycopg2.connect(
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port="5432",
            database=os.getenv("POSTGRES_DB", "best_base")
        )
        
        # Open a cursor to perform database operations
        cursor = connection.cursor()
        
        print("Connecting to base. Creating tables...")
        
        # Execute the SQL command to create tables
        cursor.execute(CREATE_TABLES_SQL)
        
        connection.commit()
        print("Tables created!")

    except (Exception, Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Connection to database has been closed.")

if __name__ == "__main__":
    create_database_schema()