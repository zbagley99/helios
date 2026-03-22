"""JSON error handlers for FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Register JSON error handlers for common HTTP errors."""

    @app.exception_handler(404)
    def not_found(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "Not found"})

    @app.exception_handler(422)
    def unprocessable(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=422, content={"error": "Validation error"})

    @app.exception_handler(500)
    def internal_error(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
