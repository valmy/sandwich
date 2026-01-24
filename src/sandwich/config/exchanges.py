"""Exchange configuration for pair matching."""

from typing import TypedDict, NotRequired


class ExchangeConfig(TypedDict):
    """Configuration for a single exchange."""
    quote: str
    match_with: NotRequired[str]


EXCHANGE_CONFIG: dict[str, ExchangeConfig] = {
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


def get_config(exchange_id: str) -> ExchangeConfig:
    """
    Get configuration for an exchange.

    Args:
        exchange_id: Exchange identifier (e.g., "binance", "hyperliquid")

    Returns:
        Exchange configuration dict

    Raises:
        ValueError: If exchange_id is not found
    """
    if exchange_id not in EXCHANGE_CONFIG:
        raise ValueError(f"Unknown exchange: {exchange_id}")
    return EXCHANGE_CONFIG[exchange_id]
