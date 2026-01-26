from typing import Optional


class SandwichError(Exception):
    """Base exception for sandwich application"""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class FileOperationError(SandwichError):
    """Raised when file operations fail"""

    def __init__(self, filename: str, operation: str, details: Optional[str] = None):
        message = f"Failed to {operation} file {filename}"
        super().__init__(message, details)


class APIRequestError(SandwichError):
    """Raised when API requests fail"""

    def __init__(
        self,
        endpoint: str,
        operation: str,
        details: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        message = f"Failed to {operation} API endpoint {endpoint}"
        if status_code:
            message += f" (status code: {status_code})"
        super().__init__(message, details)


class ConfigurationError(SandwichError):
    """Raised when configuration is invalid"""

    def __init__(self, config_key: str, reason: str, details: Optional[str] = None):
        message = f"Invalid configuration for '{config_key}': {reason}"
        super().__init__(message, details)


class ValidationError(SandwichError):
    """Raised when data validation fails"""

    def __init__(self, field: str, reason: str, details: Optional[str] = None):
        message = f"Validation error for '{field}': {reason}"
        super().__init__(message, details)


class ExchangeError(SandwichError):
    """Raised when exchange operations fail"""

    def __init__(
        self,
        exchange_id: str,
        operation: str,
        details: Optional[str] = None
    ):
        message = f"Failed to {operation} on exchange {exchange_id}"
        super().__init__(message, details)


class PairMatchingError(SandwichError):
    """Raised when pair matching operations fail"""

    def __init__(
        self,
        source_exchange: str,
        target_exchange: str,
        reason: str,
        details: Optional[str] = None
    ):
        message = f"Failed to match pairs from {source_exchange} to {target_exchange}: {reason}"
        super().__init__(message, details)


class MarketDataError(SandwichError):
    """Raised when market data operations fail"""

    def __init__(self, operation: str, details: Optional[str] = None):
        message = f"Failed to {operation} market data"
        super().__init__(message, details)
