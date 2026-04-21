from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import date
from database import get_db
from schemas import AvailableDesk

router = APIRouter(
    prefix="/desks",
    tags=["desks"]
)

@router.get("/available/", response_model=List[AvailableDesk])
def search_available_desks(
    city: str, 
    target_date: date, 
    db: Session = Depends(get_db)
):
    try:
        query = text("""
            SELECT 
                d.id AS desk_id, 
                d.label, 
                d.equipment, 
                f.level AS floor_level, 
                b.name AS building_name, 
                l.city
            FROM desk d
            JOIN floor f ON d.floor_id = f.id
            JOIN building b ON f.building_id = b.id
            JOIN location l ON b.location_id = l.id
            WHERE l.city = :city
              AND d.status != 'maintenance'
              AND NOT EXISTS (
                  SELECT 1 
                  FROM reservation r 
                  WHERE r.desk_id = d.id 
                    AND :target_date BETWEEN CAST(r.start_time AS DATE) AND CAST(r.end_time AS DATE)
              )
            ORDER BY b.name, f.level, d.label
        """)
        
        result = db.execute(query, {"city": city, "target_date": target_date}).fetchall()
        
        return [
            AvailableDesk(
                desk_id=row.desk_id,
                label=row.label,
                equipment=row.equipment,
                floor_level=row.floor_level,
                building_name=row.building_name,
                city=row.city
            ) for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching available desks")