"""Exchange configuration for pair matching."""

EXCHANGE_CONFIG: dict[str, dict] = {
    "binance": {
        "quote": "USDT",
    },
    "hyperliquid": {
        "quote": "USDC",
        "match_with": "binance",
    },
    "aster": {
        "quote": "USDC",
        "match_with": "binance",
    },
}


def get_config(exchange_id: str) -> dict:
    """
    Get configuration for an exchange.

    Args:
        exchange_id: Exchange identifier (e.g., "binance", "hyperliquid")

    Returns:
        Dict with exchange configuration

    Raises:
        ValueError: If exchange_id is not found
    """
    if exchange_id not in EXCHANGE_CONFIG:
        raise ValueError(f"Unknown exchange: {exchange_id}")
    return EXCHANGE_CONFIG[exchange_id]
