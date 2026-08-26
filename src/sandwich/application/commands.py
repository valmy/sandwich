from sandwich.infrastructure.api.coingecko import CoinGeckoClient
from sandwich.infrastructure.api.exchanges import ExchangeClient
from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.repositories.pair_repository import PairRepository
from sandwich.repositories.market_repository import MarketRepository
from sandwich.domain.services import PairMatcher, MarketDataSorter
from sandwich.domain.models import ExchangeId, MarketType
from sandwich.domain.exceptions import (
    MarketDataError,
    ExchangeError,
    PairMatchingError,
)
from sandwich.config.exchanges import get_config

logger = get_logger(__name__)


class FetchMarketDataCommand:
    """Command to fetch market data from CoinGecko"""

    def __init__(
        self,
        api_client: CoinGeckoClient,
        market_repository: MarketRepository,
        settings: Settings,
    ) -> None:
        self.api_client = api_client
        self.market_repository = market_repository
        self.settings = settings

    def execute(self) -> None:
        """Fetch and save market data"""
        try:
            logger.info("Fetching market data from CoinGecko...")
            file_path = str(self.settings.data_dir / self.settings.marketcap_file)
            market_data = self.api_client.fetch_market_data(file_path)
            self.market_repository.save_market_data(market_data)
            logger.info(f"Successfully saved {len(market_data)} market data items")
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            raise MarketDataError(
                operation="fetch and save market data",
                details=str(e)
            )


class FetchPairsCommand:
    """Command to fetch pairs from exchange"""

    def __init__(
        self,
        exchange_client: ExchangeClient,
        pair_repository: PairRepository,
        settings: Settings,
    ) -> None:
        self.exchange_client = exchange_client
        self.pair_repository = pair_repository
        self.settings = settings

    def execute(self, base_currency: str, market_type: MarketType) -> None:
        """Fetch and save pairs from exchange"""
        try:
            logger.info(
                f"Fetching pairs from {self.exchange_client.exchange_id.value} "
                f"for {base_currency} {market_type.value}"
            )
            pairs = self.exchange_client.fetch_pairs(base_currency, market_type)

            pair_strings = [pair.symbol for pair in pairs]

            self.pair_repository.save_tradingview_pairs(
                pair_strings,
                self.exchange_client.exchange_id.value,
                base_currency,
                market_type,
            )

            logger.info(f"Successfully saved {len(pairs)} pairs")
        except Exception as e:
            logger.error(f"Failed to fetch pairs: {e}")
            raise ExchangeError(
                exchange_id=self.exchange_client.exchange_id.value,
                operation=f"fetch {base_currency} {market_type.value} pairs",
                details=str(e)
            )


class MatchPairsCommand:
    """Command to match pairs between exchanges"""

    def __init__(
        self,
        pair_matcher: PairMatcher,
        pair_repository: PairRepository,
        settings: Settings,
    ) -> None:
        self.pair_matcher = pair_matcher
        self.pair_repository = pair_repository
        self.settings = settings

    def execute(
        self,
        target_exchange_id: ExchangeId,
        target_base_currency: str,
        target_market_type: MarketType,
    ) -> list[str]:
        """
        Match source exchange pairs with target exchange pairs.

        Args:
            target_exchange_id: Target exchange for matching (e.g., Hyperliquid)
            target_base_currency: Target base currency (e.g., USDT)
            target_market_type: Target market type (e.g., SWAP)

        Returns:
            List of matched pair symbols
        """
        try:
            config = get_config(target_exchange_id.value)

            if "match_with" in config:
                # Exchange needs pair matching against another exchange.
                # Source: the match_with exchange's pairs (e.g., Binance USDT
                # perps). Target: this exchange's own listings (e.g.,
                # Hyperliquid USDC swaps).
                match_with_exchange = config["match_with"]
                logger.info(
                    f"Matching {match_with_exchange} pairs against "
                    f"{target_exchange_id.value}"
                )
                source_base = target_base_currency
                target_base = config["quote"]
            else:
                # Exchange stands alone (TradingView-supported)
                logger.info(f"Processing {target_exchange_id.value} pairs")
                source_base = target_base_currency
                target_base = config["quote"]

            source_market_type = target_market_type

            source_filename = self.settings.get_pairs_filename(
                source_base, source_market_type.value, is_hyperliquid=False
            )

            target_filename = self.settings.get_pairs_filename(
                target_base, target_market_type.value, is_hyperliquid=False
            )

            source_pairs_ccxt = self.pair_repository.load_ccxt_pairs(source_filename)
            target_pairs_ccxt = self.pair_repository.load_ccxt_pairs(target_filename)

            # Validate that loaded pairs have the expected market type
            for pair in source_pairs_ccxt:
                if pair.market_type != target_market_type:
                    logger.warning(
                        f"Market type mismatch for {pair.symbol}: "
                        f"expected {target_market_type}, got {pair.market_type}"
                    )

            for pair in target_pairs_ccxt:
                if pair.market_type != target_market_type:
                    logger.warning(
                        f"Market type mismatch for {pair.symbol}: "
                        f"expected {target_market_type}, got {pair.market_type}"
                    )

            # If target doesn't exist, fetch it from the target exchange
            if not target_pairs_ccxt:
                target_exchange = target_exchange_id
                try:
                    exchange_client = ExchangeClient(self.settings, target_exchange)
                    fetch_cmd = FetchPairsCommand(
                        exchange_client,
                        self.pair_repository,
                        self.settings,
                    )
                    fetch_cmd.execute(target_base, source_market_type)
                    target_pairs_ccxt = self.pair_repository.load_ccxt_pairs(
                        target_filename
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to fetch pairs from {target_exchange.value}: {e}"
                    )
                    raise ExchangeError(
                        exchange_id=target_exchange.value,
                        operation=f"fetch {target_base} {source_market_type.value} pairs",
                        details=str(e)
                    )

            result = self.pair_matcher.match_pairs(
                source_pairs_ccxt,
                target_pairs_ccxt,
                target_exchange_id.value,
                target_base,
            )

            # Convert matched pairs to TradingView format with BINANCE prefix
            matched_symbols = []
            for pair in result.matched_pairs:
                # Always use BINANCE prefix for TradingView
                # Use original base and quote from the matched pair
                output_base = pair.base
                output_quote = pair.quote

                # Create TradingView format symbol
                if pair.market_type == MarketType.SWAP:
                    tradingview_symbol = f"{output_base}{output_quote}.P"
                else:
                    tradingview_symbol = f"{output_base}{output_quote}"

                matched_symbols.append(f"BINANCE:{tradingview_symbol}")

            hype_filename = self.settings.get_pairs_filename(
                target_base_currency, target_market_type.value, is_hyperliquid=True
            )

            self.pair_repository.save_tradingview_pairs(
                matched_symbols,
                "BINANCE",
                target_base_currency,
                target_market_type,
                filename=hype_filename,
            )

            return matched_symbols

        except Exception as e:
            logger.error(f"Failed to match pairs: {e}")
            raise PairMatchingError(
                source_exchange=target_exchange_id.value,
                target_exchange=config.get("match_with", "self"),
                reason="Pair matching operation failed",
                details=str(e)
            )


class SortPairsCommand:
    """Command to sort pairs by market volume"""

    def __init__(
        self,
        market_sorter: MarketDataSorter,
        pair_repository: PairRepository,
    ) -> None:
        self.market_sorter = market_sorter
        self.pair_repository = pair_repository

    def execute(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> None:
        """Sort pairs by market volume"""
        try:
            logger.info(
                f"Sorting {base_currency} {market_type} pairs "
                f"({'hyperliquid' if is_hyperliquid else 'regular'})"
            )

            sorted_data, sorted_count, unsorted_count = (
                self.market_sorter.sort_pairs_by_volume(
                    base_currency,
                    market_type,
                    is_hyperliquid,
                )
            )

            self.pair_repository.save_sorted_pairs(
                sorted_data, base_currency, market_type, is_hyperliquid
            )

            logger.info(
                f"Successfully sorted {sorted_count} pairs ({unsorted_count} unsorted)"
            )

        except Exception as e:
            logger.error(f"Failed to sort pairs: {e}")
            raise MarketDataError(
                operation=f"sort {base_currency} {market_type} pairs",
                details=str(e)
            )
