class SandwichError(Exception):
    """Base exception for sandwich application"""

    pass


class FileOperationError(SandwichError):
    """Raised when file operations fail"""

    pass


class APIRequestError(SandwichError):
    """Raised when API requests fail"""

    pass


class ConfigurationError(SandwichError):
    """Raised when configuration is invalid"""

    pass


class DataValidationError(SandwichError):
    """Raised when data validation fails"""

    pass


class ExchangeError(SandwichError):
    """Raised when exchange operations fail"""

    pass
