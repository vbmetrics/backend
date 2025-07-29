from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List

from . import models
from . import schemas
from .database import SessionLocal #, engine

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"Status": "Connected to DB"}

@app.get("/api/matches", response_model=List[schemas.Match])
def get_matches(db: Session = Depends(get_db)):
    matches = db.query(models.Match).options(
        joinedload(models.Match.home_team),
        joinedload(models.Match.away_team)
    ).all()
    return matches

@app.get("/api/players") # TODO
def get_players(db: Session = Depends(get_db)):
    players = []
    return players

@app.post("/api/players/add") # TODO
def add_player():
    return
