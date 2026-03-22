from typing import Optional, List
import psycopg2
from psycopg2 import Error
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db_connection

router = APIRouter(
    prefix="/company",
    tags=["company"]
)

class CompanyCreate(BaseModel):
    name: str
    group_name: Optional[str] = None
    
class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    group_name: Optional[str] = None

class Company(BaseModel):
    id: int
    name: str
    group_name: Optional[str] = None


@router.get("/", response_model=List[Company])
def get_company():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, group_name FROM company")
            companies = cursor.fetchall()
            return [Company(id=row[0], name=row[1], group_name=row[2]) for row in companies]
    except Error as e:
        raise HTTPException(status_code=500, detail="Error fetching company")
    finally:
        if 'connection' in locals():
            connection.close()

@router.post("/create/", response_model=Company)
def create_company(company: CompanyCreate):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO company (name, group_name) VALUES (%s, %s) RETURNING id",
                (company.name, company.group_name)
            )
            company_id = cursor.fetchone()[0]
            connection.commit()
            return Company(id=company_id, name=company.name, group_name=company.group_name)
    except psycopg2.IntegrityError as e:
        if 'connection' in locals():
            connection.rollback()
        raise HTTPException(status_code=400, detail="Company with this name already exists")
    except Error as e:
        if 'connection' in locals():
            connection.rollback()
        raise HTTPException(status_code=500, detail="Error creating company")
    finally:
        if 'connection' in locals():
            connection.close()

@router.patch("/{company_id}/", response_model=Company)
def update_company(company_id: int, company: CompanyUpdate):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE company SET name = %s, group_name = %s WHERE id = %s RETURNING id",
                (company.name, company.group_name, company_id)
            )
            updated_row = cursor.fetchone()
            if not updated_row:
                raise HTTPException(status_code=404, detail="Company not found")
            connection.commit()
            return Company(id=updated_row[0], name=company.name, group_name=company.group_name)
    except psycopg2.IntegrityError as e:
        if 'connection' in locals():
            connection.rollback()
        raise HTTPException(status_code=400, detail="Company with this name already exists")
    except Error as e:
        if 'connection' in locals():
            connection.rollback()
        raise HTTPException(status_code=500, detail="Error updating company")
    finally:
        if 'connection' in locals():
            connection.close()

@router.delete("/{company_id}/")
def delete_company(company_id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM company WHERE id = %s RETURNING id", (company_id,))
            deleted_row = cursor.fetchone()
            if not deleted_row:
                raise HTTPException(status_code=404, detail="Company not found")
            connection.commit()
            return {"detail": "Company deleted successfully"}
    except Error as e:
        if 'connection' in locals():
            connection.rollback()
        raise HTTPException(status_code=500, detail="Error deleting company")
    finally:
        if 'connection' in locals():
            connection.close()