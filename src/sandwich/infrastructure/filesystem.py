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
        # Precompute exchange prefixes for faster checking
        self.exchange_prefixes = {exchange.value.upper(): exchange for exchange in ExchangeId}

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
            # Join all lines first and write once for better performance
            lines = []
            for pair in pairs:
                # Check if pair already has valid exchange prefix
                has_exchange_prefix = False
                if ":" in pair:
                    prefix = pair.split(":", 1)[0].upper()
                    if prefix in self.exchange_prefixes:
                        has_exchange_prefix = True
                        lines.append(f"{pair}\n")
                        continue
                
                # Format as TradingView format
                symbol = pair.replace("/", "")
                for quote_currency in self.settings.QUOTE_CURRENCIES:
                    if symbol.endswith(f":{quote_currency}"):
                        symbol = symbol[: -len(f":{quote_currency}")]
                        break
                lines.append(f"{exchange_id_upper}:{symbol}{type_str}\n")
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)

            logger.info(
                f"Saved {len(pairs)} {exchange_id} {base_currency} {market_type.value} "
                f"pairs to {filename}"
            )
        except (IOError, OSError) as e:
            raise FileOperationError(
                filename=filename,
                operation="save pairs",
                details=str(e)
            )

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
                # Use generator expression for memory efficiency
                pairs = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(pairs)} pairs from {filename}")
            return pairs
        except (IOError, OSError) as e:
            raise FileOperationError(
                filename=filename,
                operation="read pairs",
                details=str(e)
            )

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
            raise FileOperationError(
                filename=filename,
                operation="save sorted pairs",
                details=str(e)
            )

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
                data = json.load(f)  # More efficient than json.loads(f.read())

            logger.info(f"Loaded {len(data)} market data items")
            return data[:500]  # Support up to 500 items with 2 pages
        except json.JSONDecodeError as e:
            raise FileOperationError(
                filename=self.settings.marketcap_file,
                operation="parse market data",
                details=str(e)
            )
        except (IOError, OSError) as e:
            raise FileOperationError(
                filename=self.settings.marketcap_file,
                operation="read market data",
                details=str(e)
            )
