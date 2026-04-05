"""Structured JSON logging using stdlib logging with a custom JSONFormatter."""

import json
import logging
import traceback
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = getattr(record, "payload", {})
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            "payload": payload,
        }
        if record.exc_info:
            entry["traceback"] = traceback.format_exception(*record.exc_info)
        return json.dumps(entry)


def get_logger(name: str = "tradingview_alpaca") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


logger = get_logger()
