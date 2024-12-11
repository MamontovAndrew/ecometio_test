import uvicorn
from fastapi import FastAPI
from app.api.v1 import api_router
from app.core.database import Database
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title="GitHub Top100 API", version="1.0.0")

app.include_router(api_router, prefix=settings.API_V1_STR)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await Database.connect()

@app.on_event("shutdown")
async def shutdown():
    await Database.close()
    await Database.check_tables_exist()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)