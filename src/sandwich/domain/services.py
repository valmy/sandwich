from typing import List, Dict, Set, TYPE_CHECKING

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import TradingPair, PairMatchResult, ExchangeId

if TYPE_CHECKING:
    from sandwich.infrastructure.api.coingecko import CoinGeckoClient
    from sandwich.repositories.market_repository import MarketRepository
    from sandwich.repositories.pair_repository import PairRepository

logger = get_logger(__name__)


class PairMatcher:
    """Service for matching pairs between exchanges"""

    # Currency equivalence mapping
    CURRENCY_EQUIVALENCE = {
        "USDC": "USDT",
        "USDT": "USDC",
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def normalize_coin_name(self, coin: str) -> str:
        """
        Normalize coin names by handling special prefixes.

        Args:
            coin: Coin name (e.g., KPEPE, 1000PEPE)

        Returns:
            Normalized coin name (e.g., PEPE)
        """
        if not coin or len(coin) < 2:
            return coin

        if (
            (coin.startswith("k") or coin.startswith("K"))
            and len(coin) > 1
            and coin[1].isupper()
        ):
            return coin[1:]

        if coin.startswith("1000") and len(coin) > 4:
            return coin[4:]

        return coin

    def match_pairs(
        self,
        source_pairs: List[TradingPair],
        target_pairs: List[TradingPair],
        source_exchange: str = "source",
        target_exchange: str = "target",
    ) -> PairMatchResult:
        """
        Match pairs between source and target exchanges.

        Args:
            source_pairs: Pairs from source exchange
            target_pairs: Pairs from target exchange
            source_exchange: Source exchange name (for logging)
            target_exchange: Target exchange name (for logging)

        Returns:
            PairMatchResult with matched and missing pairs
        """
        # Create a set of normalized target bases for O(1) lookups
        target_normalized = set()
        for pair in target_pairs:
            normalized_base = self.normalize_coin_name(pair.base)
            target_normalized.add(normalized_base)
            
            # Add mapped currency (e.g., USDT ↔ USDC)
            mapped_base = self.CURRENCY_EQUIVALENCE.get(pair.base)
            if mapped_base and mapped_base != pair.base:
                mapped_normalized = self.normalize_coin_name(mapped_base)
                target_normalized.add(mapped_normalized)

        matched_pairs: List[TradingPair] = []
        missing_pairs: List[TradingPair] = []
        special_matches = 0
        normal_matches = 0

        for source_pair in source_pairs:
            normalized_base = self.normalize_coin_name(source_pair.base)

            # Check direct match
            matched = normalized_base in target_normalized

            # Check mapped currency (e.g., source is USDT, target has USDC)
            if not matched:
                mapped_base = self.CURRENCY_EQUIVALENCE.get(source_pair.base)
                if mapped_base:
                    normalized_mapped = self.normalize_coin_name(mapped_base)
                    matched = normalized_mapped in target_normalized

            if matched:
                matched_pairs.append(source_pair)

                # Check for special prefix matches or currency mapping matches
                is_currency_mapping = (
                    source_pair.base in self.CURRENCY_EQUIVALENCE
                    and self.CURRENCY_EQUIVALENCE[source_pair.base] != source_pair.base
                )

                if source_pair.base != normalized_base or is_currency_mapping:
                    special_matches += 1
                    match_type = "currency mapping" if is_currency_mapping else "prefix"
                    logger.debug(
                        f"Special match: {source_pair.base} ({source_exchange}) [{match_type}]"
                    )
                else:
                    normal_matches += 1
            else:
                missing_pairs.append(source_pair)

        if missing_pairs:
            logger.info(
                f"Pairs in {source_exchange} but not in {target_exchange}: "
                f"{len(missing_pairs)}"
            )

        logger.info(
            f"Matched {len(matched_pairs)} pairs between {source_exchange} "
            f"and {target_exchange}"
        )
        logger.info(f"  - Normal matches: {normal_matches}")
        logger.info(f"  - Special prefix matches: {special_matches}")

        return PairMatchResult(
            matched_pairs=matched_pairs,
            missing_pairs=missing_pairs,
            normal_matches=normal_matches,
            special_matches=special_matches,
        )


class MarketDataSorter:
    """Service for sorting market data"""

    def __init__(
        self, 
        settings: Settings, 
        coingecko_client: 'CoinGeckoClient',
        market_repository: 'MarketRepository',
        pair_repository: 'PairRepository'
    ) -> None:
        self.settings = settings
        self.coingecko_client = coingecko_client
        self.market_repository = market_repository
        self.pair_repository = pair_repository

    def load_stablecoins(self) -> Set[str]:
        """Load stablecoins from CoinGecko"""
        stablecoins_file = str(
            self.settings.data_dir / self.settings.get_stablecoins_filename()
        )
        return self.coingecko_client.fetch_stablecoins(stablecoins_file)

    def load_market_data(self) -> List[dict]:
        """Load market data from repository"""
        return [m.model_dump() for m in self.market_repository.load_market_data()]

    def load_pair_lines(self, filename: str) -> List[str]:
        """Load pair lines from repository"""
        return self.pair_repository.load_pair_lines(filename)

    def remove_prefix_suffix(self, s: str) -> str:
        """
        Remove exchange prefix and .P suffix from string.

        Args:
            s: Input string

        Returns:
            String with prefix and suffix removed
        """
        # Remove any exchange prefix (e.g., BINANCE:, HYPERLIQUID:, etc.)
        for exchange in ExchangeId:
            prefix = f"{exchange.value.upper()}:"
            if s.startswith(prefix):
                s = s.replace(prefix, "", 1)
                break
        # Remove .P suffix (perpetual)
        if s.endswith(".P"):
            s = s[:-2]
        return s

    def create_symbol_index(self, lines: List[str]) -> Dict[str, str]:
        """
        Create an index of normalized symbols to their original lines for O(1) lookups.

        Args:
            lines: List of trading pair lines

        Returns:
            Dictionary mapping normalized symbol to original line
        """
        symbol_index = {}
        for line in lines:
            normalized_symbol = self.remove_prefix_suffix(line).upper()
            symbol_index[normalized_symbol] = line
            # Also handle 1000 prefix case for quick lookups
            if normalized_symbol.startswith("1000"):
                without_prefix = normalized_symbol[4:]
                if without_prefix not in symbol_index:
                    symbol_index[without_prefix] = line
        return symbol_index

    def find_symbol_in_index(
        self,
        market_data_item: dict,
        symbol_index: Dict[str, str],
        base_currency: str,
        stablecoins: Set[str],
        check_excluded_currencies: bool = True,
    ) -> str:
        """
        Find matching trading pair line for a market data item using an index.

        Args:
            market_data_item: Market data item with 'symbol' field
            symbol_index: Pre-created index of normalized symbols to lines
            base_currency: Base currency to match
            stablecoins: Set of stablecoin symbols to filter out
            check_excluded_currencies: Whether to filter excluded currencies

        Returns:
            Matching line or empty string if not found
        """
        if not isinstance(market_data_item, dict) or "symbol" not in market_data_item:
            return ""

        symbol_value = market_data_item["symbol"]
        if symbol_value is None:
            return ""

        symbol = symbol_value.upper() + base_currency
        symbol_upper = symbol_value.upper()

        # Check if symbol is a stablecoin
        if symbol_upper in stablecoins:
            logger.debug(f"Filtering out stablecoin: {symbol_upper}")
            return ""

        # O(1) lookup in the index
        if symbol in symbol_index:
            line = symbol_index[symbol]
            if check_excluded_currencies:
                if not any(symbol == f"{curr}{base_currency}" for curr in self.settings.EXCLUDED_CURRENCIES):
                    return line
            else:
                return line

        return ""

    def sort_pairs_by_volume(
        self,
        base_currency: str,
        market_type: str,
        is_hyperliquid: bool = False,
    ) -> tuple[str, int, int]:
        """
        Sort trading pairs by market volume.

        Args:
            base_currency: Base currency
            market_type: Market type
            is_hyperliquid: Whether this is hyperliquid data

        Returns:
            Tuple of (sorted_data_string, sorted_count, unsorted_count)
        """
        # Load dependencies
        stablecoins = self.load_stablecoins()
        market_data = self.load_market_data()
        
        filename = self.settings.get_pairs_filename(
            base_currency, market_type, is_hyperliquid
        )
        pairs_lines = self.load_pair_lines(filename)

        # Create symbol index for O(1) lookups (O(n) pre-processing time)
        symbol_index = self.create_symbol_index(pairs_lines)

        # Filter and validate market data
        valid_market_data = []
        for item in market_data:
            if (
                isinstance(item, dict)
                and "symbol" in item
                and "total_volume" in item
                and item["symbol"] is not None
                and item["total_volume"] is not None
            ):
                # Validate that total_volume is numeric
                try:
                    volume = float(item["total_volume"])
                    if volume >= 0:  # Ensure non-negative volume
                        valid_market_data.append(item)
                except (ValueError, TypeError):
                    logger.warning(
                        f"Invalid volume data for {item.get('symbol', 'unknown')}: "
                        f"{item.get('total_volume')}"
                    )
                    continue

        market_data_sorted = sorted(
            valid_market_data, key=lambda x: x["total_volume"], reverse=True
        )

        sorted_lines = []
        sorted_symbols: set = set()
        filtered_stablecoins_count = 0
        filtered_stablecoin_lines: set = set()

        for item in market_data_sorted:
            symbol_upper = item.get("symbol", "").upper()
            line = self.find_symbol_in_index(
                item, symbol_index, base_currency, stablecoins
            )
            if line:
                sorted_lines.append(line)
                sorted_symbols.add(line)
            elif symbol_upper in stablecoins:
                # Symbol was filtered because it's a stablecoin
                # Find the matching line (without stablecoin or excluded currency filter) to exclude from unsorted
                stablecoin_line = self.find_symbol_in_index(
                    item,
                    symbol_index,
                    base_currency,
                    set(),
                    check_excluded_currencies=False,
                )
                if stablecoin_line:
                    filtered_stablecoin_lines.add(stablecoin_line)
                    filtered_stablecoins_count += 1

        unsorted_count = 0
        for line in pairs_lines:
            if line not in sorted_symbols and line not in filtered_stablecoin_lines:
                sorted_lines.append(line)
                unsorted_count += 1

        sorted_count = len(sorted_symbols)
        sorted_data = "\n".join(sorted_lines) + "\n"

        logger.info(f"Sorted {sorted_count} pairs by volume")
        logger.info(f"Unsorted pairs: {unsorted_count}")
        if filtered_stablecoins_count > 0:
            logger.info(f"Filtered out {filtered_stablecoins_count} stablecoin pairs")

        return sorted_data, sorted_count, unsorted_count
