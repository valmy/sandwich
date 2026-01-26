"""Output formatting for CLI commands."""

from enum import Enum
from typing import Any, Optional
import json
from sandwich.domain.exceptions import SandwichError


class OutputFormat(str, Enum):
    """Supported output formats."""

    TEXT = "text"
    JSON = "json"


class OutputFormatter:
    """Formats output for CLI commands."""

    def __init__(self, format: OutputFormat = OutputFormat.TEXT):
        self.format = format

    def format_success(self, data: Any, message: Optional[str] = None) -> str:
        """Format successful command execution output."""
        if self.format == OutputFormat.JSON:
            output = {
                "success": True,
                "data": data,
            }
            if message:
                output["message"] = message
            return json.dumps(output, ensure_ascii=False, indent=2, default=str)
        else:
            if message:
                return message
            return str(data)

    def format_error(self, error: Exception, message: Optional[str] = None) -> str:
        """Format error output."""
        if self.format == OutputFormat.JSON:
            error_data = {
                "success": False,
                "error": str(error),
            }
            if message:
                error_data["message"] = message
            if isinstance(error, SandwichError) and error.details:
                error_data["details"] = error.details
            return json.dumps(error_data, ensure_ascii=False, indent=2, default=str)
        else:
            if message:
                return f"Error: {message}\n{error}"
            return f"Error: {error}"
