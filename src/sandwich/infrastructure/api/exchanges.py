import ccxt
from typing import List, Optional, Any

from .base import BaseAPIClient
from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import TradingPair, ExchangeId, MarketType
from sandwich.domain.exceptions import ExchangeError

logger = get_logger(__name__)


class ExchangeClient(BaseAPIClient):
    """CCXT-based exchange client"""

    def __init__(self, settings: Settings, exchange_id: ExchangeId, cache_manager: Optional[Any] = None) -> None:
        super().__init__(settings)
        self.exchange_id = exchange_id
        self.cache_manager = cache_manager

        try:
            exchange_class = getattr(ccxt, exchange_id.value)
            config: dict[str, Any] = {}
            if exchange_id == ExchangeId.HYPERLIQUID:
                # ccxt's hyperliquid spot-market parser fails on unmapped
                # tokens; only swap listings are needed for pair matching
                config["options"] = {"fetchMarkets": {"types": ["swap"]}}
            self.exchange = exchange_class(config)
            logger.info(f"Initialized {exchange_id.value} exchange client")
        except AttributeError:
            raise ExchangeError(
                exchange_id=exchange_id.value,
                operation="initialize exchange client",
                details=f"Exchange '{exchange_id.value}' not found in ccxt"
            )
        except Exception as e:
            raise ExchangeError(
                exchange_id=exchange_id.value,
                operation="initialize exchange client",
                details=str(e)
            )

    def fetch_pairs(
        self, base_currency: str, market_type: MarketType
    ) -> List[TradingPair]:
        """
        Fetch trading pairs from exchange with exponential backoff retry logic and caching.

        Args:
            base_currency: Quote currency to filter by (e.g., USDT, USDC)
            market_type: Type of market (swap or spot)

        Returns:
            List of trading pairs

        Raises:
            ExchangeError: If fetching fails after all retries
        """
        import time

        logger.info(
            f"Fetching {self.exchange_id.value} {base_currency} {market_type.value} pairs"
        )

        # Try to get data from cache
        if self.cache_manager:
            cached_data = self.cache_manager.get(
                self.fetch_pairs, base_currency, market_type
            )
            if cached_data is not None:
                logger.info(f"Loaded {self.exchange_id.value} pairs from cache")
                pairs = [TradingPair(**item) for item in cached_data]
                logger.info(f"Found {len(pairs)} active pairs (from cache)")
                return pairs

        for attempt in range(self.settings.max_retries):
            try:
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

                # Cache the raw dict data for easy serialization
                if self.cache_manager:
                    raw_data = [item.model_dump() for item in pairs]
                    self.cache_manager.set(
                        self.fetch_pairs, raw_data, base_currency, market_type
                    )

                return pairs

            except Exception as e:
                logger.error(
                    f"Failed to fetch pairs from {self.exchange_id.value} on attempt {attempt + 1}: {e}"
                )
                
                if attempt < self.settings.max_retries - 1:
                    delay = 2 ** attempt
                    logger.warning(
                        f"Retrying in {delay} seconds (attempt {attempt + 2}/{self.settings.max_retries})"
                    )
                    time.sleep(delay)

        logger.error(f"Max retries ({self.settings.max_retries}) exhausted")
        raise ExchangeError(
            exchange_id=self.exchange_id.value,
            operation=f"fetch {base_currency} {market_type.value} pairs",
            details=f"Failed after {self.settings.max_retries} attempts"
        )
