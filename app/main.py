from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.v1 import api_router as api_v1_router

app = FastAPI(
    title="vbmetrics API",
    description="API for vbmetrics, a tool for analyzing volleyball data.",
    version="1.0",
)

register_error_handlers(app)

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

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to vbmetrics API!"}
