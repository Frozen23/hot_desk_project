from fastapi import FastAPI
from routers import company
 

app = FastAPI(title="Hot Desk") 

app.include_router(company.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) #reload=True is for development only, remove it in production 