from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import timezone
from database import get_db
from schemas import ReservationCreate, Reservation

router = APIRouter(
	prefix="/reservation",
	tags=["reservation"]
)


@router.post("/", response_model=Reservation, status_code=201)
async def create_reservation(reservation: ReservationCreate, db: AsyncSession = Depends(get_db)):
	try:
		start_time = reservation.start_time
		end_time = reservation.end_time

		if start_time.tzinfo is not None:
			start_time = start_time.astimezone(timezone.utc).replace(tzinfo=None)
		if end_time.tzinfo is not None:
			end_time = end_time.astimezone(timezone.utc).replace(tzinfo=None)

		if end_time <= start_time:
			raise HTTPException(status_code=400, detail="End time must be after start time")

		desk_query = text("""
			SELECT id, status
			FROM desk
			WHERE id = :desk_id
		""")
		desk_result = await db.execute(desk_query, {"desk_id": reservation.desk_id})
		desk_row = desk_result.fetchone()

		if not desk_row:
			raise HTTPException(status_code=404, detail="Desk not found")
		if desk_row.status == "maintenance":
			raise HTTPException(status_code=400, detail="Desk is under maintenance")

		employee_query = text("""
			SELECT id
			FROM employee
			WHERE id = :employee_id
		""")
		employee_result = await db.execute(employee_query, {"employee_id": reservation.employee_id})
		employee_row = employee_result.fetchone()

		if not employee_row:
			raise HTTPException(status_code=404, detail="Employee not found")

		conflict_query = text("""
			SELECT 1
			FROM reservation
			WHERE desk_id = :desk_id
			  AND :start_time < end_time
			  AND :end_time > start_time
			LIMIT 1
		""")
		conflict_result = await db.execute(
			conflict_query,
			{
				"desk_id": reservation.desk_id,
				"start_time": start_time,
				"end_time": end_time,
			},
		)

		if conflict_result.fetchone():
			raise HTTPException(status_code=400, detail="Desk is already reserved for this time range")

		insert_query = text("""
			INSERT INTO reservation (desk_id, employee_id, start_time, end_time, status)
			VALUES (:desk_id, :employee_id, :start_time, :end_time, :status)
			RETURNING id, desk_id, employee_id, start_time, end_time, status, created_at
		""")

		result = await db.execute(
			insert_query,
			{
				"desk_id": reservation.desk_id,
				"employee_id": reservation.employee_id,
				"start_time": start_time,
				"end_time": end_time,
				"status": reservation.status,
			},
		)
		new_reservation = result.fetchone()
		await db.commit()

		return Reservation(
			id=new_reservation.id,
			desk_id=new_reservation.desk_id,
			employee_id=new_reservation.employee_id,
			start_time=new_reservation.start_time,
			end_time=new_reservation.end_time,
			status=new_reservation.status,
			created_at=new_reservation.created_at,
		)

	except HTTPException:
		await db.rollback()
		raise
	except Exception:
		await db.rollback()
		raise HTTPException(status_code=500, detail="Error creating reservation")
