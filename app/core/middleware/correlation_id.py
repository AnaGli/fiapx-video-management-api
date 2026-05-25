import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import bind_log_context, reset_log_context, set_log_context


class CorrelationIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        tokens = bind_log_context(
            correlation_id=correlation_id,
            request_method=request.method,
            request_path=str(request.url.path),
        )

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            set_log_context(
                request_status=response.status_code,
                request_duration_ms=duration_ms,
            )
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            reset_log_context(tokens)