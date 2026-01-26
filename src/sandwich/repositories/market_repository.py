from typing import List

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.filesystem import FilesystemOperations
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.models import MarketData
from sandwich.domain.exceptions import FileOperationError
import json

logger = get_logger(__name__)


class MarketRepository:
    """Repository for market data"""

    def __init__(self, settings: Settings, filesystem: FilesystemOperations) -> None:
        self.settings = settings
        self.filesystem = filesystem

    def load_market_data(self) -> List[MarketData]:
        """
        Load market data from file.

        Returns:
            List of MarketData objects
        """
        data = self.filesystem.load_market_data()
        return [MarketData(**item) for item in data]

    def save_market_data(self, market_data: List[MarketData]) -> None:
        """
        Save market data to file.

        Args:
            market_data: List of MarketData objects

        Raises:
            FileOperationError: If save fails
        """
        filepath = self.settings.data_dir / self.settings.marketcap_file

        try:
            with open(filepath, "w") as f:
                json.dump([m.model_dump() for m in market_data], f)
            logger.info(f"Saved {len(market_data)} market data items")
        except (IOError, OSError, TypeError) as e:
            raise FileOperationError(
                filename=self.settings.marketcap_file,
                operation="save market data",
                details=str(e)
            )
