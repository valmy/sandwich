from sandwich.domain.exceptions import ValidationError
from sandwich.domain.models import MarketType, ExchangeId


def validate_market_type(market_type: str) -> MarketType:
    """Validate market type"""
    try:
        return MarketType(market_type.lower())
    except ValueError:
        raise ValidationError(
            field="market_type",
            reason="Invalid market type",
            details=f"{market_type} is not valid. Must be 'swap' or 'spot'"
        )


def validate_exchange_id(exchange_id: str) -> ExchangeId:
    """Validate exchange ID"""
    try:
        return ExchangeId(exchange_id.lower())
    except ValueError:
        raise ValidationError(
            field="exchange_id",
            reason="Invalid exchange ID",
            details=f"{exchange_id} is not valid. Supported: {[e.value for e in ExchangeId]}"
        )


def parse_base_and_market_type(base_param: str) -> tuple[str, MarketType]:
    """Parse base parameter and extract base currency and market type"""
    if not base_param:
        raise ValidationError(
            field="base_param",
            reason="Base parameter cannot be empty"
        )

    base_param = base_param.lower()

    if base_param.endswith("perp"):
        base_currency = base_param[:-4].upper()
        market_type = MarketType.SWAP
    else:
        base_currency = base_param.upper()
        market_type = MarketType.SPOT

    return base_currency, market_type
