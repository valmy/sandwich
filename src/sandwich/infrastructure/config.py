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

    def get_pairs_filename(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> str:
        """Generate pairs filename"""
        suffix = "_hype_pairs" if is_hyperliquid else "_pairs"
        filename = f"{base_currency.lower()}_{market_type}{suffix}.txt"

        # Fallback: if file doesn't exist or is empty, try "perp" instead of "swap"
        filepath = self.data_dir / filename
        if market_type == "swap":
            if not filepath.exists():
                # File doesn't exist, try "perp" variant
                fallback_filename = f"{base_currency.lower()}_perp{suffix}.txt"
                if (self.data_dir / fallback_filename).exists():
                    return fallback_filename
            elif filepath.exists() and filepath.stat().st_size == 0:
                # File is empty, try "perp" variant
                fallback_filename = f"{base_currency.lower()}_perp{suffix}.txt"
                if (self.data_dir / fallback_filename).exists():
                    return fallback_filename

        return filename

    def get_sorted_filename(
        self, base_currency: str, market_type: str, is_hyperliquid: bool = False
    ) -> str:
        """Generate sorted filename"""
        suffix = "_hype" if is_hyperliquid else ""
        return f"sorted_{base_currency.lower()}_{market_type}{suffix}.txt"
