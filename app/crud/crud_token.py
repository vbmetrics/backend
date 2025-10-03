from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast

from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.token import RefreshToken
from app.schemas.token import RefreshTokenCreateDTO, RefreshTokenUpdateDTO


class CRUDRefreshToken(
    CRUDBase[RefreshToken, RefreshTokenCreateDTO, RefreshTokenUpdateDTO]
):
    def get_by_jti(self, db: Session, jti: str) -> RefreshToken | None:
        stmt = select(self.model).where(self.model.jti == jti)
        return db.exec(stmt).first()

    def get_active_for_user(
        self, db: Session, user_id, now: datetime
    ) -> Sequence[RefreshToken]:
        # mypy-safe columns
        uid_col: Any = self.model.user_id
        revoked_col: Any = self.model.revoked_at
        exp_col: Any = self.model.expires_at

        stmt = select(self.model).where(
            uid_col == user_id,
            revoked_col.is_(None),  # type: ignore[attr-defined]
            exp_col > now,  # type: ignore[operator]
        )
        return cast(Sequence[RefreshToken], db.exec(stmt).all())


refresh_token = CRUDRefreshToken(RefreshToken)
