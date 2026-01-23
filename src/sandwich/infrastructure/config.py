from pydantic import Field, PrivateAttr
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar, Dict


class Settings(BaseSettings):
    """Application configuration"""

    data_dir: Path = Field(default=Path.cwd(), description="Data directory")
    marketcap_file: str = Field(
        default="marketcap.json", description="Market data file"
    )

    coingecko_api_url: str = Field(
        default="https://api.coingecko.com/api/v3/coins/markets",
        description="CoinGecko API base URL",
    )
    max_retries: int = Field(
        default=5, ge=1, le=10, description="Max API retry attempts"
    )
    items_per_page: int = Field(
        default=250, ge=1, le=500, description="Items per API page"
    )
    pages_to_fetch: int = Field(
        default=2, ge=1, le=10, description="Number of pages to fetch"
    )

    base_currency: str = Field(default="USDT", description="Default base currency")

    stablecoins_file: str = Field(
        default="stablecoins.json", description="Cached stablecoins file"
    )

    EXCLUDED_CURRENCIES: ClassVar[list[str]] = ["USDC", "FDUSD", "EUR"]
    QUOTE_CURRENCIES: ClassVar[list[str]] = ["FDUSD", "USDT", "USDC"]

    # Instance-specific cache for filenames to avoid repeated I/O
    _filename_cache: Dict[str, str] = PrivateAttr(default_factory=dict)

    def get_pairs_filename(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> str:
        """Generate pairs filename"""
        # Sanitize inputs to prevent path traversal
        import re

        safe_base_currency = re.sub(r"[^a-zA-Z0-9]", "", base_currency).lower()
        safe_market_type = re.sub(r"[^a-zA-Z0-9]", "", market_type)

        # Additional validation to prevent empty strings after sanitization
        if not safe_base_currency or len(safe_base_currency) < 2:
            raise ValueError(
                "Invalid base_currency: must contain at least 2 alphanumeric characters"
            )
        if not safe_market_type or len(safe_market_type) < 2:
            raise ValueError(
                "Invalid market_type: must contain at least 2 alphanumeric characters"
            )

        cache_key = f"{safe_base_currency}_{safe_market_type}_{is_hyperliquid}"
        if cache_key in self._filename_cache:
            return self._filename_cache[cache_key]

        suffix = "_hype_pairs" if is_hyperliquid else "_pairs"
        filename = f"{safe_base_currency}_{safe_market_type}{suffix}.txt"

        # Ensure filename doesn't contain path separators and resolve to prevent traversal
        safe_filename = Path(filename).name
        if safe_filename != filename:
            raise ValueError("Invalid filename: contains path separators")

        # Fallback: if file doesn't exist or is empty, try "perp" instead of "swap"
        if safe_market_type == "swap":
            filepath = self.data_dir / safe_filename
            try:
                if not filepath.exists() or filepath.stat().st_size == 0:
                    # File doesn't exist or is empty, try "perp" variant
                    fallback_filename = f"{safe_base_currency}_perp{suffix}.txt"
                    safe_fallback = Path(fallback_filename).name
                    if safe_fallback != fallback_filename:
                        raise ValueError("Invalid fallback filename: contains path separators")
                    if (self.data_dir / safe_fallback).exists():
                        self._filename_cache[cache_key] = safe_fallback
                        return safe_fallback
            except OSError:
                # If file operations fail, return original filename
                pass

        self._filename_cache[cache_key] = safe_filename
        return safe_filename

    def get_sorted_filename(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> str:
        """Generate sorted filename"""
        # Sanitize inputs to prevent path traversal
        import re

        safe_base_currency = re.sub(r"[^a-zA-Z0-9]", "", base_currency).lower()
        safe_market_type = re.sub(r"[^a-zA-Z0-9]", "", market_type)

        # Additional validation to prevent empty strings after sanitization
        if not safe_base_currency or len(safe_base_currency) < 2:
            raise ValueError(
                "Invalid base_currency: must contain at least 2 alphanumeric characters"
            )
        if not safe_market_type or len(safe_market_type) < 2:
            raise ValueError(
                "Invalid market_type: must contain at least 2 alphanumeric characters"
            )

        suffix = "_hype" if is_hyperliquid else ""
        return f"sorted_{safe_base_currency}_{safe_market_type}{suffix}.txt"
