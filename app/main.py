from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import countries, seasons, arenas

#from .database import engine
#from . import models

#models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="vbmetrics API"
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(countries.router)
api_router.include_router(seasons.router)
api_router.include_router(arenas.router)
# TODO: other routers

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to vbmetrics API!"}
