from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar


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

    EXCLUDED_CURRENCIES: ClassVar[list[str]] = ["USDC", "FDUSD", "EUR"]

    # In-memory cache for filenames to avoid repeated I/O
    _filename_cache: ClassVar[dict[str, str]] = {}

    def get_pairs_filename(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> str:
        """Generate pairs filename"""
        # Sanitize inputs to prevent path traversal
        safe_base_currency = "".join(c for c in base_currency if c.isalnum()).lower()
        safe_market_type = "".join(c for c in market_type if c.isalnum())

        if not safe_base_currency or not safe_market_type:
            raise ValueError("Invalid base_currency or market_type")

        cache_key = f"{safe_base_currency}_{safe_market_type}_{is_hyperliquid}"
        if cache_key in self._filename_cache:
            return self._filename_cache[cache_key]

        suffix = "_hype_pairs" if is_hyperliquid else "_pairs"
        filename = f"{safe_base_currency}_{safe_market_type}{suffix}.txt"

        # Fallback: if file doesn't exist or is empty, try "perp" instead of "swap"
        if safe_market_type == "swap":
            filepath = self.data_dir / filename
            try:
                if not filepath.exists() or filepath.stat().st_size == 0:
                    # File doesn't exist or is empty, try "perp" variant
                    fallback_filename = f"{safe_base_currency}_perp{suffix}.txt"
                    if (self.data_dir / fallback_filename).exists():
                        self._filename_cache[cache_key] = fallback_filename
                        return fallback_filename
            except OSError:
                # If file operations fail, return original filename
                pass

        self._filename_cache[cache_key] = filename
        return filename

    def get_sorted_filename(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> str:
        """Generate sorted filename"""
        # Sanitize inputs to prevent path traversal
        safe_base_currency = "".join(c for c in base_currency if c.isalnum()).lower()
        safe_market_type = "".join(c for c in market_type if c.isalnum())

        if not safe_base_currency or not safe_market_type:
            raise ValueError("Invalid base_currency or market_type")

        suffix = "_hype" if is_hyperliquid else ""
        return f"sorted_{safe_base_currency}_{safe_market_type}{suffix}.txt"
