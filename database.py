import os
import psycopg2
from psycopg2 import Error
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        return psycopg2.connect(
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get("POSTGRES_DB")
        )
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    group_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS location (
    id SERIAL PRIMARY KEY,
    country VARCHAR(50),
    city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS user_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS building (
    id SERIAL PRIMARY KEY,
    location_id INT REFERENCES location(id) ON DELETE CASCADE,
    name VARCHAR(100),
    address VARCHAR(100),
    company_id INT REFERENCES company(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS work_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    company_id INT REFERENCES company(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS floor (
    id SERIAL PRIMARY KEY,
    building_id INT REFERENCES building(id) ON DELETE CASCADE,
    level INT,
    svg_path VARCHAR(255),
    width INT,
    height INT
);

CREATE TABLE IF NOT EXISTS work_group_building (
    workgroup_id INT REFERENCES work_group(id) ON DELETE CASCADE,
    building_id INT REFERENCES building(id) ON DELETE CASCADE,
    PRIMARY KEY (workgroup_id, building_id)
);

CREATE TABLE IF NOT EXISTS employee (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    user_group_id INT REFERENCES user_group(id) ON DELETE SET NULL,
    workgroup_id INT REFERENCES work_group(id) ON DELETE SET NULL,
    email VARCHAR(50) UNIQUE,
    hash_password VARCHAR(256)
);


CREATE TABLE IF NOT EXISTS desk (
    id SERIAL PRIMARY KEY,
    floor_id INT REFERENCES floor(id) ON DELETE CASCADE,
    label VARCHAR(20),
    x INT,
    y INT,
    status VARCHAR(20)
);


CREATE TABLE IF NOT EXISTS reservation (
    id SERIAL PRIMARY KEY,
    desk_id INT REFERENCES desk(id) ON DELETE CASCADE,
    employee_id INT REFERENCES employee(id) ON DELETE CASCADE,
    date DATE,
    start_time TIME,
    end_time TIME,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_database_schema():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        print("Connecting to base. Creating tables...")
        
        # Execute the SQL command to create tables
        cursor.execute(CREATE_TABLES_SQL)
        
        connection.commit()
        print("Tables created!")
    except Error as e:
        print(f"Error creating tables: {e}")
        
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
            print("Connection to database has been closed.")

if __name__ == "__main__":
    create_database_schema()