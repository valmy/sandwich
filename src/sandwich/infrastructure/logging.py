import logging
from typing import Optional
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """Setup application logging"""
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(level=level, format=log_format, handlers=handlers)


def get_logger(name: str) -> logging.Logger:
    """Get logger for a module"""
    return logging.getLogger(name)
