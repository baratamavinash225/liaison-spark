import logging
import os
import sys
from typing import Any

import structlog
from opentelemetry import trace


def extract_opentelemetry_context(
    logger: logging.Logger, log_method: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Inject OpenTelemetry trace and span IDs into the log record."""
    span = trace.get_current_span()
    if span.is_recording():
        context = span.get_span_context()
        event_dict["trace_id"] = trace.format_trace_id(context.trace_id)
        event_dict["span_id"] = trace.format_span_id(context.span_id)
    return event_dict


def setup_logging():
    """
    Configure structlog for robust production-ready logging.
    - Routes standard logging to structlog.
    - Adds OpenTelemetry tracing context.
    - Uses Console rendering in dev, and JSON rendering in production.
    """
    is_development = (
        os.environ.get("ENVIRONMENT", "development").lower() == "development"
    )

    # 1. Clear existing standard loggers (prevents double logging)
    logging.root.handlers = []

    # 2. Define shared processors for all loggers
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        extract_opentelemetry_context,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # 3. Configure structlog
    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 4. Set formatter based on environment
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(colors=True)
            if is_development
            else structlog.processors.JSONRenderer(),
        ],
    )

    # 5. Route all standard logs through our structlog formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # 6. Suppress overly verbose 3rd-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
