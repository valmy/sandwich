from typing import List

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.filesystem import FilesystemOperations
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import TradingPair, MarketType, ExchangeId

logger = get_logger(__name__)


class PairRepository:
    """Repository for trading pair data"""

    def __init__(self, settings: Settings, filesystem: FilesystemOperations) -> None:
        self.settings = settings
        self.filesystem = filesystem

    def load_tradingview_pairs(
        self, base_currency: str, market_type: MarketType, is_hyperliquid: bool = False
    ) -> List[str]:
        """Load TradingView-format pairs from file"""
        filename = self.settings.get_pairs_filename(
            base_currency, market_type.value, is_hyperliquid
        )
        return self.filesystem.load_pairs(filename)

    def load_pair_lines(self, filename: str) -> List[str]:
        """
        Load pairs from file as raw lines.

        Args:
            filename: Name of file to load from

        Returns:
            List of raw line strings
        """
        return self.filesystem.load_pairs(filename)

    def load_ccxt_pairs(self, filename: str) -> List[TradingPair]:
        """
        Load pairs from file and convert to CCXT format.

        Args:
            filename: Name of file to load from

        Returns:
            List of TradingPair objects
        """
        lines = self.filesystem.load_pairs(filename)
        pairs: List[TradingPair] = []

        for line in lines:
            try:
                line = line.strip()
                if not line:
                    continue

                # Handle different formats:
                # 1. TradingView: "BINANCE:BTCUSDTPERP"
                # 2. CCXT: "BTC/USDT"
                # 3. Mixed: "BTC/USDT:USDT"

                prefix = "binance"  # default
                symbol = line

                # Check if it's TradingView format (contains exchange prefix)
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        potential_prefix, symbol_part = parts
                        # Check if first part looks like an exchange name
                        if potential_prefix.upper() in [
                            "BINANCE",
                            "HYPERLIQUID",
                            "BYBIT",
                            "OKX",
                        ]:
                            prefix = potential_prefix.upper()
                            symbol = symbol_part
                        # Handle mixed format like "BTC/USDT:USDT"
                        elif (
                            "/" in potential_prefix
                            and len(potential_prefix.split("/")) == 2
                        ):
                            symbol = potential_prefix  # Use "BTC/USDT" part

                # Remove PERP suffix
                is_swap = False
                symbol_upper = symbol.upper()
                if symbol_upper.endswith("PERP"):
                    symbol = symbol[:-4]
                    symbol_upper = symbol.upper()
                    is_swap = True

                # Extract base and quote
                base = None
                quote = None

                # First try CCXT format: "BTC/USDT"
                if "/" in symbol:
                    base, quote = symbol.split("/", 1)
                    base = base.strip()
                    quote = quote.strip()
                else:
                    # TradingView format: "BTCUSDT" - match longest suffix first
                    currencies = ["FDUSD", "USDT", "USDC"]
                    for curr in currencies:
                        if symbol_upper.endswith(curr.upper()):
                            quote = curr
                            base = symbol_upper[: -len(curr)]
                            break

                if base is None or quote is None:
                    logger.warning(
                        f"Failed to parse base/quote from symbol '{symbol}' (line: '{line}')"
                    )
                    continue

                # Map prefix to ExchangeId enum
                exchange_map = {
                    "BINANCE": ExchangeId.BINANCE,
                    "HYPERLIQUID": ExchangeId.HYPERLIQUID,
                    "BYBIT": ExchangeId.BYBIT,
                    "OKX": ExchangeId.OKX,
                }
                exchange_id = exchange_map.get(prefix.upper(), ExchangeId.BINANCE)

                market_type = MarketType.SWAP if is_swap else MarketType.SPOT

                pairs.append(
                    TradingPair(
                        symbol=f"{base}/{quote}",
                        base=base,
                        quote=quote,
                        exchange=exchange_id,
                        market_type=market_type,
                        is_active=True,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse line '{line}': {e}")
                continue

        logger.info(f"Parsed {len(pairs)} CCXT-format pairs from {filename}")
        return pairs

    def save_tradingview_pairs(
        self,
        pairs: List[str],
        exchange_id: str,
        base_currency: str,
        market_type: MarketType,
        filename: str | None = None,
    ) -> None:
        """Save pairs in TradingView format"""
        self.filesystem.save_pairs_for_tradingview(
            pairs, exchange_id, base_currency, market_type, filename
        )
