from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.services.errors import APIError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_app_error(_: Request, exc: APIError) -> JSONResponse:
        payload = {
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        }
        return JSONResponse(status_code=exc.http_status, content=payload)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        payload = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),  # pydantic error structure
            }
        }
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload
        )

    @app.exception_handler(404)
    async def handle_404(_: Request, __) -> JSONResponse:
        payload = {
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "details": None,
            }
        }
        return JSONResponse(status_code=404, content=payload)

    @app.exception_handler(IntegrityError)
    async def integrity_error_exception_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        # Pozwala to json.dumps sparsować to bez problemu.
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

        payload = {
            "error": "IntegrityError",
            "detail": "Database constraint violation.",
            "message": error_msg
        }

        return JSONResponse(status_code=409, content=payload)
