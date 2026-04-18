from fastapi import FastAPI
from database import create_database_schema
from routers import company

create_database_schema()

app = FastAPI(title="Hot Desk API") 

app.include_router(company.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)