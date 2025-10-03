from sqlmodel import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    now_utc,
    verify_password,
)
from app.crud.crud_token import refresh_token as rt_crud
from app.crud.crud_user import user as user_crud
from app.schemas.token import RefreshTokenCreateDTO
from app.services.errors import UnauthorizedError


class AuthService:
    def login(
        self,
        db: Session,
        *,
        email: str,
        password: str,
        user_agent: str | None,
        ip: str | None,
    ) -> tuple[str, str, int]:
        """
        Returns (access_token, refresh_token, access_expires_in_seconds).
        """
        u = user_crud.get_by_email(db, email)
        if not u or not u.is_active or not verify_password(password, u.hashed_password):
            raise UnauthorizedError("Invalid credentials", code="INVALID_CREDENTIALS")

        # Safety: ensure user persisted ID exists (non-null UUID)
        if u.id is None:
            raise RuntimeError("User must have an ID before creating tokens")

        access, expires_in = create_access_token(str(u.id), extra={"role": u.role})
        refresh_token, jti, exp = create_refresh_token(str(u.id))

        rt_dto = RefreshTokenCreateDTO(
            jti=jti,
            user_id=u.id,  # safe: checked above
            user_agent=user_agent,
            ip_address=ip,
            expires_at=exp,
            revoked_at=None,
        )
        rt_crud.create(db, obj_in=rt_dto)

        return access, refresh_token, expires_in

    def refresh(self, db: Session, *, refresh_token: str) -> tuple[str, str, int]:
        """
        Rotate refresh token, return new (access, refresh, access_expires_in).
        """
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise UnauthorizedError("Invalid refresh token", code="INVALID_REFRESH")

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type", code="INVALID_REFRESH_TYPE")

        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub:
            raise UnauthorizedError("Malformed token", code="INVALID_REFRESH")

        record = rt_crud.get_by_jti(db, jti)
        if record is None or not record.is_active(now_utc()):
            raise UnauthorizedError(
                "Refresh token revoked or expired", code="REFRESH_INACTIVE"
            )

        # Revoke old refresh token (rotation)
        record.revoked_at = now_utc()
        db.add(record)
        db.commit()
        db.refresh(record)

        access, expires_in = create_access_token(sub)

        # Safety: ensure foreign key is present
        if record.user_id is None:
            raise RuntimeError("Refresh token record has no user_id")

        new_refresh, new_jti, new_exp = create_refresh_token(sub)
        new_rt_dto = RefreshTokenCreateDTO(
            jti=new_jti,
            user_id=record.user_id,  # safe: checked above
            user_agent=None,
            ip_address=None,
            expires_at=new_exp,
            revoked_at=None,
        )
        rt_crud.create(db, obj_in=new_rt_dto)

        return access, new_refresh, expires_in

    def logout(self, db: Session, *, refresh_token: str) -> None:
        """
        Revoke given refresh token if valid; idempotent.
        """
        try:
            payload = decode_token(refresh_token)
        except Exception:
            return  # idempotent on invalid token

        jti = payload.get("jti")
        if not jti:
            return

        record = rt_crud.get_by_jti(db, jti)
        if record and record.revoked_at is None:
            record.revoked_at = now_utc()
            db.add(record)
            db.commit()
