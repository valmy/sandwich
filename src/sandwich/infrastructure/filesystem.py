from typing import List, Optional

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import MarketType, ExchangeId
from sandwich.domain.exceptions import FileOperationError

logger = get_logger(__name__)


class FilesystemOperations:
    """File I/O operations"""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def save_pairs_for_tradingview(
        self,
        pairs: List[str],
        exchange_id: str,
        base_currency: str,
        market_type: MarketType,
        filename: Optional[str] = None,
    ) -> None:
        """
        Save pairs in TradingView format.

        Args:
            pairs: List of pair strings
            exchange_id: Exchange identifier
            base_currency: Base currency
            market_type: Market type
            filename: Optional filename (auto-generated if not provided)

        Raises:
            FileOperationError: If file operation fails
        """
        if filename is None:
            filename = self.settings.get_pairs_filename(
                base_currency, market_type.value, is_hyperliquid=False
            )

        filepath = self.settings.data_dir / filename
        type_str = ".P" if market_type == MarketType.SWAP else ""
        exchange_id_upper = exchange_id.upper()

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for pair in pairs:
                    # If pair already contains exchange prefix, use it as-is
                    # Check for valid exchange prefixes from ExchangeId enum
                    # CCXT format like "BTC/USDT:USDT" has colon but not exchange prefix
                    has_exchange_prefix = False
                    for exchange in ExchangeId:
                        if pair.startswith(f"{exchange.value.upper()}:"):
                            has_exchange_prefix = True
                            break

                    if has_exchange_prefix:
                        tradingview_format = f"{pair}\n"
                    else:
                        # Otherwise, format it (convert from CCXT format)
                        # Remove quote currency suffixes using suffix matching (not replace)
                        # to avoid issues with currency names appearing within other names
                        symbol = pair.replace("/", "")
                        for quote_currency in self.settings.QUOTE_CURRENCIES:
                            if symbol.endswith(f":{quote_currency}"):
                                symbol = symbol[: -len(f":{quote_currency}")]
                                break
                        tradingview_format = f"{exchange_id_upper}:{symbol}{type_str}\n"
                    f.write(tradingview_format)

            logger.info(
                f"Saved {len(pairs)} {exchange_id} {base_currency} {market_type.value} "
                f"pairs to {filename}"
            )
        except (IOError, OSError) as e:
            raise FileOperationError(f"Failed to save pairs to {filename}: {e}")

    def load_pairs(self, filename: str) -> List[str]:
        """
        Load pairs from file.

        Args:
            filename: Name of file to load from

        Returns:
            List of pair strings (empty list if file doesn't exist)

        Raises:
            FileOperationError: If file read fails (except FileNotFoundError)
        """
        filepath = self.settings.data_dir / filename

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                pairs = [line.strip() for line in f.readlines() if line.strip()]
            logger.info(f"Loaded {len(pairs)} pairs from {filename}")
            return pairs
        except (IOError, OSError) as e:
            raise FileOperationError(f"Failed to read {filename}: {e}")

    def save_sorted_pairs(
        self,
        sorted_data: str,
        base_currency: str,
        market_type: str,
        is_hyperliquid: bool = False,
    ) -> None:
        """
        Save sorted pairs to file.

        Args:
            sorted_data: String containing sorted pairs
            base_currency: Base currency
            market_type: Market type
            is_hyperliquid: Whether this is hyperliquid data

        Raises:
            FileOperationError: If file operation fails
        """
        filename = self.settings.get_sorted_filename(
            base_currency, market_type, is_hyperliquid
        )
        filepath = self.settings.data_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(sorted_data)
            logger.info(f"Saved sorted pairs to {filename}")
        except (IOError, OSError) as e:
            raise FileOperationError(f"Failed to save sorted pairs: {e}")

    def load_market_data(self) -> list[dict]:
        """
        Load market data from JSON file.

        Returns:
            List of market data dictionaries (empty list if file doesn't exist)

        Raises:
            FileOperationError: If file read fails (except FileNotFoundError)
        """
        import json

        filepath = self.settings.data_dir / self.settings.marketcap_file

        if not filepath.exists():
            logger.warning(f"Market data file not found: {filepath}")
            return []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.loads(f.read())

            logger.info(f"Loaded {len(data)} market data items")
            return data[:500]  # Support up to 500 items with 2 pages
        except json.JSONDecodeError as e:
            raise FileOperationError(f"Invalid JSON in market data file: {e}")
        except (IOError, OSError) as e:
            raise FileOperationError(f"Failed to read market data: {e}")
