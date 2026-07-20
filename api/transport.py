"""FastAPI HTTP/SSE transport over the approved read-only API service."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .dtos import SignalEventDTO
from .service import ReadOnlyApiService, SignalNotFoundError


APP_VERSION = "api.v1"
APPROVED_EVENT_TYPES = {"new_signal", "weakening", "invalidation", "stale_data"}


def error_envelope(code: str, message: str, request_id: str | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if request_id:
        error["request_id"] = request_id
    return {"error": error}


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def format_sse(event: SignalEventDTO) -> str:
    """Format one approved event using SSE event/data framing."""

    if event.event_type not in APPROVED_EVENT_TYPES:
        raise ValueError("unsupported_event_type")
    payload = json.dumps(event.to_dict(), ensure_ascii=False, separators=(",", ":"))
    return f"event: {event.event_type}\ndata: {payload}\n\n"


def create_app(service: ReadOnlyApiService, event_source: Callable[[], Iterable[Mapping[str, Any]]] | None = None) -> FastAPI:
    """Create an app with injected read-only dependencies; no default live clients."""

    app = FastAPI(title="Yaobi Long Signal API", version=APP_VERSION)
    app.state.read_only_service = service
    app.state.event_source = event_source or (lambda: ())

    def get_service() -> ReadOnlyApiService:
        return app.state.read_only_service

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=error_envelope("invalid_request", "请求参数无效。", _request_id(request)))

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "not_found" if exc.status_code == 404 else "invalid_request" if 400 <= exc.status_code < 500 else "internal_error"
        message = "未找到请求的资源。" if code == "not_found" else "请求无效。" if code == "invalid_request" else "服务内部错误。"
        return JSONResponse(status_code=exc.status_code, content=error_envelope(code, message, _request_id(request)))

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=error_envelope("internal_error", "服务内部错误。", _request_id(request)))

    @app.get("/api/v1/dashboard")
    def dashboard(api_service: ReadOnlyApiService = Depends(get_service)) -> dict[str, Any]:
        return api_service.dashboard().to_dict()

    @app.get("/api/v1/signals/history")
    def signal_history(api_service: ReadOnlyApiService = Depends(get_service)) -> dict[str, Any]:
        return {"api_version": APP_VERSION, "signals": [item.to_dict() for item in api_service.history()]}

    @app.get("/api/v1/signals/{signal_id}")
    def signal_detail(signal_id: str, api_service: ReadOnlyApiService = Depends(get_service)) -> dict[str, Any]:
        try:
            return api_service.signal_detail(signal_id).to_dict()
        except SignalNotFoundError as exc:
            raise StarletteHTTPException(status_code=404) from exc

    @app.get("/api/v1/signals/{signal_id}/outcomes")
    def signal_outcomes(signal_id: str, api_service: ReadOnlyApiService = Depends(get_service)) -> dict[str, Any]:
        try:
            api_service.signal_detail(signal_id)
            return {"api_version": APP_VERSION, "signal_id": signal_id, "outcomes": [item.to_dict() for item in api_service.outcomes(signal_id)]}
        except SignalNotFoundError as exc:
            raise StarletteHTTPException(status_code=404) from exc

    @app.get("/api/v1/statistics/summary")
    def statistics(api_service: ReadOnlyApiService = Depends(get_service)) -> dict[str, Any]:
        return api_service.statistics().to_dict()

    @app.get("/api/v1/health")
    def health(api_service: ReadOnlyApiService = Depends(get_service)) -> dict[str, Any]:
        return {"api_version": APP_VERSION, "health": [item.to_dict() for item in api_service.health()]}

    @app.get("/api/v1/events")
    async def events() -> StreamingResponse:
        messages = service.event_messages(app.state.event_source())

        async def stream():
            for message in messages:
                if message.event_type in APPROVED_EVENT_TYPES:
                    yield format_sse(message)

        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    return app
