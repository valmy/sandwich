import json
from typing import List, Optional

from .base import BaseAPIClient
from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import MarketData
from sandwich.domain.exceptions import APIRequestError

logger = get_logger(__name__)


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
