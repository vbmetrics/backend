from collections.abc import Generator

from sqlmodel import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
