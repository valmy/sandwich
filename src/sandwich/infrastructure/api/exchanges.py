import ccxt
from typing import List

from .base import BaseAPIClient
from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import TradingPair, ExchangeId, MarketType
from sandwich.domain.exceptions import ExchangeError

logger = get_logger(__name__)


class ExchangeClient(BaseAPIClient):
    """CCXT-based exchange client"""

    def __init__(self, settings: Settings, exchange_id: ExchangeId) -> None:
        super().__init__(settings)
        self.exchange_id = exchange_id

        try:
            exchange_class = getattr(ccxt, exchange_id.value)
            self.exchange = exchange_class()
            logger.info(f"Initialized {exchange_id.value} exchange client")
        except AttributeError:
            raise ExchangeError(f"Exchange '{exchange_id.value}' not found in ccxt")
        except Exception as e:
            raise ExchangeError(f"Failed to initialize {exchange_id.value}: {e}")

    def fetch_pairs(
        self, base_currency: str, market_type: MarketType
    ) -> List[TradingPair]:
        """
        Fetch trading pairs from exchange.

        Args:
            base_currency: Quote currency to filter by (e.g., USDT, USDC)
            market_type: Type of market (swap or spot)

        Returns:
            List of trading pairs

        Raises:
            ExchangeError: If fetching fails
        """
        try:
            logger.info(
                f"Fetching {self.exchange_id.value} {base_currency} {market_type.value} pairs"
            )

            markets = self.exchange.load_markets()

            pairs = [
                TradingPair(
                    symbol=symbol,
                    base=market["base"],
                    quote=market["quote"],
                    exchange=self.exchange_id,
                    market_type=market_type,
                    is_active=market["active"],
                )
                for symbol, market in markets.items()
                if market["active"]
                and market["quote"] == base_currency.upper()
                and market.get(market_type.value, False)
            ]

            logger.info(f"Found {len(pairs)} active pairs")
            return pairs

        except Exception as e:
            logger.error(f"Failed to fetch pairs from {self.exchange_id.value}: {e}")
            raise ExchangeError(f"Failed to fetch pairs: {e}")
