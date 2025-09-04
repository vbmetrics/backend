from collections.abc import Mapping
from typing import Any, Optional


class APIError(Exception):
    """
    Base class for all domain API errors.
    """

    http_status: int = 500  # default, override in subclasses
    code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code  # allow per-instance override
        self.details = dict(details) if details else None


class NotFoundError(APIError):
    http_status = 404
    code = "NOT_FOUND"


class BadRequestError(APIError):
    http_status = 400
    code = "BAD_REQUEST"


class ConflictError(APIError):
    http_status = 409
    code = "CONFLICT"


class UnauthorizedError(APIError):
    http_status = 401
    code = "UNAUTHORIZED"


class ForbiddenError(APIError):
    http_status = 403
    code = "FORBIDDEN"


class PreconditionFailedError(APIError):
    http_status = 412
    code = "PRECONDITION_FAILED"
