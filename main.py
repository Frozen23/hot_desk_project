from fastapi import FastAPI

from routers import company
 

app = FastAPI(title="Hot Desk") 

app.include_router(company.router)