from pydantic import BaseModel, Field, field_validator
from enum import Enum


class MarketType(str, Enum):
    SWAP = "swap"
    SPOT = "spot"


class ExchangeId(str, Enum):
    BINANCE = "binance"
    HYPERLIQUID = "hyperliquid"
    BYBIT = "bybit"
    OKX = "okx"


class TradingPair(BaseModel):
    """Represents a trading pair from an exchange"""

    symbol: str = Field(..., description="Full symbol including quote currency")
    base: str = Field(..., description="Base currency (e.g., BTC)")
    quote: str = Field(..., description="Quote currency (e.g., USDT)")
    exchange: ExchangeId = Field(..., description="Exchange identifier")
    market_type: MarketType = Field(..., description="Market type")
    is_active: bool = Field(True, description="Whether that pair is active")

    @field_validator("symbol", "base", "quote")
    @classmethod
    def uppercase(cls, v: str) -> str:
        return v.upper()


class MarketData(BaseModel):
    """Represents market data from CoinGecko"""

    id: str = Field(..., description="Coin identifier")
    symbol: str = Field(..., description="Coin symbol")
    current_price: float = Field(..., ge=0, description="Current price in USD")
    total_volume: float = Field(..., ge=0, description="24h trading volume")
    market_cap: float = Field(..., ge=0, description="Market capitalization")
    market_cap_rank: int = Field(..., ge=1, description="Market cap rank")

    @field_validator("symbol")
    @classmethod
    def uppercase(cls, v: str) -> str:
        return v.upper()


class PairMatchResult(BaseModel):
    """Result of matching pairs between exchanges"""

    matched_pairs: list[TradingPair]
    missing_pairs: list[TradingPair]
    normal_matches: int
    special_matches: int
