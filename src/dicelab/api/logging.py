"""Structured (JSON-ish) logging configuration."""

from __future__ import annotations

from logging.config import dictConfig


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "format": '{"level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
                }
            },
            "handlers": {
                "default": {"class": "logging.StreamHandler", "formatter": "json"}
            },
            "root": {"handlers": ["default"], "level": "INFO"},
        }
    )
