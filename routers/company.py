from typing import Optional, List
import psycopg2
from psycopg2 import Error
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from database import get_db

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
def get_company(connection=Depends(get_db)):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, group_name FROM company")
            return [Company(id=row[0], name=row[1], group_name=row[2]) for row in cursor]
    except Error as e:
        raise HTTPException(status_code=500, detail="Error fetching company")

@router.post("/", response_model=Company)
def create_company(company: CompanyCreate, connection=Depends(get_db)):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO company (name, group_name) VALUES (%s, %s) RETURNING id",
                (company.name, company.group_name)
            )
            connection.commit()
            return Response(status_code=201)
    except psycopg2.IntegrityError as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=400, detail="Company with this name already exists")
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail="Error creating company")

@router.patch("/{company_id}/", response_model=Company)
def update_company(company_id: int, company: CompanyUpdate, connection=Depends(get_db)):
    try:
        with connection.cursor() as cursor:

            update_data = company.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            set_clauses = [f"{field} = %s" for field in update_data.keys()]
            set_clause = ", ".join(set_clauses)
            values = list(update_data.values())

            values.append(company_id)

            query = f"UPDATE company SET {set_clause} WHERE id = %s RETURNING id, name, group_name"
            
            cursor.execute(query, values)
            updated_row = cursor.fetchone()
            if not updated_row:
                raise HTTPException(status_code=404, detail="Company not found")
            connection.commit()
            return Company(id=updated_row[0], name=updated_row[1], group_name=updated_row[2])
        
    except psycopg2.IntegrityError as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=400, detail="Company with this name already exists")
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail="Error updating company")

@router.delete("/{company_id}/")
def delete_company(company_id: int, connection=Depends(get_db)):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM company WHERE id = %s RETURNING id", (company_id,))
            deleted_row = cursor.fetchone()
            if not deleted_row:
                raise HTTPException(status_code=404, detail="Company not found")
            connection.commit()
            return Response(status_code=204)
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail="Error deleting company")