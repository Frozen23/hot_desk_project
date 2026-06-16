from fastapi import FastAPI
from database import create_database_schema
from routers import company
from routers import desks
from routers import reservation


app = FastAPI(title="Hot Desk API") 

app.include_router(company.router)
app.include_router(desks.router)
app.include_router(reservation.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)