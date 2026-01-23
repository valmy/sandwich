import json
from typing import List, Optional, Set
from pathlib import Path
import time

from .base import BaseAPIClient
from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import MarketData
from sandwich.domain.exceptions import APIRequestError

logger = get_logger(__name__)

CACHE_EXPIRY_HOURS = 24


class CoinGeckoClient(BaseAPIClient):
    """CoinGecko API client"""

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.api_url = settings.coingecko_api_url

    def fetch_market_data(self, file_path: Optional[str] = None) -> List[MarketData]:
        """
        Fetch market data from CoinGecko API.

        Args:
            file_path: Optional file path to save data to

        Returns:
            List of market data objects

        Raises:
            APIRequestError: If API request fails
        """
        all_data: list[dict] = []

        for page in range(1, self.settings.pages_to_fetch + 1):
            page_url = f"{self.api_url}?vs_currency=usd&per_page={self.settings.items_per_page}&page={page}"
            logger.info(f"Fetching page {page}: {page_url}")

            response = self.make_request(page_url)
            if response is None or response.status_code != 200:
                raise APIRequestError(f"Failed to fetch page {page}")

            try:
                data = response.json()
            except ValueError as e:
                raise APIRequestError(f"Invalid JSON response from page {page}: {e}")
            all_data.extend(data)
            logger.debug(f"Fetched {len(data)} items from page {page}")

        logger.info(f"Total items fetched: {len(all_data)}")

        market_data = [MarketData(**item) for item in all_data[:500]]

        if file_path:
            self._save_to_file(market_data, file_path)

        return market_data

    def _save_to_file(self, market_data: List[MarketData], file_path: str) -> None:
        """Save market data to JSON file"""
        logger.info(f"Saving market data to {file_path}")

        try:
            with open(file_path, "w") as f:
                json.dump([m.model_dump() for m in market_data], f)
            logger.info(f"Successfully saved {len(market_data)} items to {file_path}")
        except (IOError, OSError) as e:
            raise APIRequestError(f"Failed to save market data: {e}")

    def fetch_stablecoins(self, file_path: Optional[str] = None) -> Set[str]:
        """
        Fetch list of stablecoin symbols from CoinGecko.

        Note: The CoinGecko free API doesn't support category filtering.
        This method uses a hardcoded list of common stablecoins as a fallback.

        Args:
            file_path: Optional file path to cache stablecoins data

        Returns:
            Set of stablecoin symbols (uppercase)
        """
        # Check cache first
        if file_path:
            cache_file = Path(file_path)
            if cache_file.exists():
                try:
                    file_age = time.time() - cache_file.stat().st_mtime
                    if file_age < CACHE_EXPIRY_HOURS * 3600:
                        logger.info(f"Loading stablecoins from cache: {file_path}")
                        with open(cache_file, "r") as f:
                            cached_data = json.load(f)
                        stablecoins = set(s.upper() for s in cached_data)
                        logger.info(f"Loaded {len(stablecoins)} stablecoins from cache")
                        return stablecoins
                    else:
                        logger.info(
                            f"Cache is older than {CACHE_EXPIRY_HOURS} hours, using fresh list"
                        )
                except (IOError, OSError, json.JSONDecodeError) as e:
                    logger.warning(f"Failed to read stablecoins cache: {e}")

        # Use hardcoded list of common stablecoins (CoinGecko free API doesn't support categories)
        logger.info("Using hardcoded list of common stablecoins")
        stablecoins = {
            # USD stablecoins
            "USDT",
            "USDC",
            "DAI",
            "TUSD",
            "USDD",
            "USDP",
            "USDe",
            "FDUSD",
            "PYUSD",
            "cUSDT",
            "cUSDC",
            "aUSDT",
            "aUSDC",
            "USDC.E",
            "USDT.E",
            # EUR stablecoins
            "EURS",
            "EURC",
            "EUROC",
            "EURT",
            "sEUR",
            # GBP stablecoins
            "GBPT",
            "GBPC",
            # CNY stablecoins
            "CNHT",
            "CNYT",
            # JPY stablecoins
            "JPYT",
            "JPYC",
            # Other stablecoins
            "XAUT",
            "USDX",
            "DYAD",
            "GHO",
            "crvUSD",
            "LUSD",
            "RAI",
            "sUSD",
            "USDN",
            "USDS",
            "USTC",
            "HAY",
            "BOB",
            "Fei",
            "OHM",
            "SPELL",
            "SUSD",
            "USDK",
            "USX",
            "USDV",
            "VAI",
            "ZUSD",
        }

        logger.info(f"Using {len(stablecoins)} stablecoins from hardcoded list")

        # Save to cache if file_path provided
        if file_path:
            self._save_stablecoins_to_file(list(stablecoins), file_path)

        return stablecoins

    def _save_stablecoins_to_file(self, stablecoins: List[str], file_path: str) -> None:
        """Save stablecoins list to JSON file"""
        logger.info(f"Saving stablecoins to {file_path}")

        try:
            with open(file_path, "w") as f:
                json.dump(stablecoins, f)
            logger.info(f"Successfully saved {len(stablecoins)} stablecoins to {file_path}")
        except (IOError, OSError) as e:
            raise APIRequestError(f"Failed to save stablecoins: {e}")
