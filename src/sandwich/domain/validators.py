from sandwich.domain.exceptions import DataValidationError
from sandwich.domain.models import MarketType, ExchangeId


def validate_base_currency(currency: str) -> str:
    """Validate and normalize base currency"""
    if not currency or not isinstance(currency, str):
        raise DataValidationError(f"Invalid base currency: {currency}")

    base_currency = currency.replace("PERP", "").upper()

    if not base_currency or not base_currency.isalpha():
        raise DataValidationError(f"Base currency must be alphabetic: {currency}")

    return base_currency


def validate_market_type(market_type: str) -> MarketType:
    """Validate market type"""
    try:
        return MarketType(market_type.lower())
    except ValueError:
        raise DataValidationError(
            f"Invalid market type: {market_type}. Must be 'swap' or 'spot'"
        )


def validate_exchange_id(exchange_id: str) -> ExchangeId:
    """Validate exchange ID"""
    try:
        return ExchangeId(exchange_id.lower())
    except ValueError:
        raise DataValidationError(
            f"Invalid exchange ID: {exchange_id}. "
            f"Supported: {[e.value for e in ExchangeId]}"
        )


def parse_base_and_market_type(base_param: str) -> tuple[str, MarketType]:
    """Parse base parameter and extract base currency and market type"""
    if not base_param:
        raise DataValidationError("Base parameter cannot be empty")

    base_param = base_param.lower()

    if base_param.endswith("perp"):
        base_currency = base_param[:-4].upper()
        market_type = MarketType.SWAP
    else:
        base_currency = base_param.upper()
        market_type = MarketType.SPOT

    return base_currency, market_type
