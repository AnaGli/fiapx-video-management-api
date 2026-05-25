import logging
import os
import sys
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

try:
    from ddtrace import tracer
except ImportError:
    tracer = None

_context_vars = {
    "correlation_id": ContextVar("correlation_id", default=None),
    "request_method": ContextVar("request_method", default=None),
    "request_path": ContextVar("request_path", default=None),
    "request_status": ContextVar("request_status", default=None),
    "request_duration_ms": ContextVar("request_duration_ms", default=None),
    "service_order_id": ContextVar("service_order_id", default=None),
    "business_operation": ContextVar("business_operation", default=None),
}


class DatadogContextFilter(logging.Filter):
    def filter(self, record):
        record.service = os.getenv("DD_SERVICE", "fastapi-app")
        record.env = os.getenv("DD_ENV", os.getenv("APP_ENV", "local"))
        record.version = os.getenv("DD_VERSION", "unknown")
        record.correlation_id = _context_vars["correlation_id"].get()
        record.request_method = _context_vars["request_method"].get()
        record.request_path = _context_vars["request_path"].get()
        record.request_status = _context_vars["request_status"].get()
        record.request_duration_ms = _context_vars["request_duration_ms"].get()
        record.service_order_id = _context_vars["service_order_id"].get()
        record.business_operation = _context_vars["business_operation"].get()

        record.trace_id = None
        record.span_id = None

        if tracer is not None:
            span = tracer.current_span()
            if span is not None:
                record.trace_id = getattr(span, "trace_id", None)
                record.span_id = getattr(span, "span_id", None)

        return True


def bind_log_context(**kwargs):
    tokens = []
    for key, value in kwargs.items():
        var = _context_vars[key]
        tokens.append((var, var.set(value)))
    return tokens


def reset_log_context(tokens):
    for var, token in reversed(tokens):
        var.reset(token)


def set_log_context(**kwargs):
    for key, value in kwargs.items():
        _context_vars[key].set(value)


def setup_logging():
    logger = logging.getLogger()
    logger.handlers = []
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(DatadogContextFilter())
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s "
            "%(service)s %(env)s %(version)s %(correlation_id)s "
            "%(request_method)s %(request_path)s %(request_status)s "
            "%(request_duration_ms)s %(service_order_id)s "
            "%(business_operation)s %(trace_id)s %(span_id)s"
        )
    )

    logger.addHandler(handler)