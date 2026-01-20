from typing import List, Dict

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import TradingPair, PairMatchResult, ExchangeId

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
        target_normalized: Dict[str, List[TradingPair]] = {}
        for pair in target_pairs:
            normalized_base = self.normalize_coin_name(pair.base)
            if normalized_base not in target_normalized:
                target_normalized[normalized_base] = []
            target_normalized[normalized_base].append(pair)

            # Add mapped currency (e.g., USDT ↔ USDC)
            mapped_base = self.CURRENCY_EQUIVALENCE.get(pair.base)
            if mapped_base and mapped_base != pair.base:
                mapped_normalized = self.normalize_coin_name(mapped_base)
                if mapped_normalized not in target_normalized:
                    target_normalized[mapped_normalized] = []
                target_normalized[mapped_normalized].append(pair)

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

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

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

    def find_symbol_in_lines(
        self, market_data_item: dict, lines: List[str], base_currency: str
    ) -> str:
        """
        Find matching trading pair line for a market data item.

        Args:
            market_data_item: Market data item with 'symbol' field
            lines: List of trading pair lines
            base_currency: Base currency to match

        Returns:
            Matching line or empty string if not found
        """
        if not isinstance(market_data_item, dict) or "symbol" not in market_data_item:
            return ""

        symbol_value = market_data_item["symbol"]
        if symbol_value is None:
            return ""

        symbol = symbol_value.upper() + base_currency

        for line in lines:
            symbol_in_line = self.remove_prefix_suffix(line)

            if (
                symbol == symbol_in_line.upper()
                or ("1000" + symbol.upper()) == symbol_in_line.upper()
            ):
                if not any(
                    symbol == f"{curr}{base_currency}"
                    for curr in self.settings.EXCLUDED_CURRENCIES
                ):
                    return line

        return ""

    def sort_pairs_by_volume(
        self,
        market_data: List[dict],
        pairs_lines: List[str],
        base_currency: str,
        market_type: str,
        is_hyperliquid: bool = False,
    ) -> tuple[str, int, int]:
        """
        Sort trading pairs by market volume.

        Args:
            market_data: List of market data dictionaries
            pairs_lines: List of trading pair lines
            base_currency: Base currency
            market_type: Market type
            is_hyperliquid: Whether this is hyperliquid data

        Returns:
            Tuple of (sorted_data_string, sorted_count, unsorted_count)
        """
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

        sorted_data = ""
        sorted_symbols: set = set()

        for item in market_data_sorted:
            line = self.find_symbol_in_lines(item, pairs_lines, base_currency)
            if line:
                sorted_data += line + "\n"
                sorted_symbols.add(line)

        unsorted_count = 0
        for line in pairs_lines:
            if line not in sorted_symbols:
                sorted_data += line + "\n"
                unsorted_count += 1

        sorted_count = len(sorted_symbols)

        logger.info(f"Sorted {sorted_count} pairs by volume")
        logger.info(f"Unsorted pairs: {unsorted_count}")

        return sorted_data, sorted_count, unsorted_count
