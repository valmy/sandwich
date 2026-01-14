from pathlib import Path

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import setup_logging, get_logger
from sandwich.infrastructure.filesystem import FilesystemOperations
from sandwich.infrastructure.api.coingecko import CoinGeckoClient
from sandwich.infrastructure.api.exchanges import ExchangeClient
from sandwich.repositories.pair_repository import PairRepository
from sandwich.repositories.market_repository import MarketRepository
from sandwich.domain.services import PairMatcher, MarketDataSorter
from sandwich.application.commands import (
    FetchMarketDataCommand,
    FetchPairsCommand,
    MatchPairsCommand,
    SortPairsCommand,
)
from sandwich.domain.models import ExchangeId


class DIContainer:
    """Manual dependency injection container"""

    def __init__(self, data_dir: Path | None = None) -> None:
        setup_logging()
        self.logger = get_logger(__name__)

        if data_dir:
            self.settings = Settings(data_dir=data_dir)
        else:
            self.settings = Settings()

        self.logger.info("Initializing DI container")

        self._init_infrastructure()
        self._init_repositories()
        self._init_services()
        self._init_commands()

    def _init_infrastructure(self) -> None:
        """Initialize infrastructure components"""
        self.logger.debug("Initializing infrastructure")

        self.filesystem = FilesystemOperations(self.settings)
        self.coingecko_client = CoinGeckoClient(self.settings)

    def _init_repositories(self) -> None:
        """Initialize repositories"""
        self.logger.debug("Initializing repositories")

        self.pair_repository = PairRepository(self.settings, self.filesystem)
        self.market_repository = MarketRepository(self.settings, self.filesystem)

    def _init_services(self) -> None:
        """Initialize domain services"""
        self.logger.debug("Initializing domain services")

        self.pair_matcher = PairMatcher(self.settings)
        self.market_sorter = MarketDataSorter(self.settings)

    def _init_commands(self) -> None:
        """Initialize use case commands"""
        self.logger.debug("Initializing commands")

        self.fetch_market_data_command = FetchMarketDataCommand(
            self.coingecko_client, self.market_repository, self.settings
        )

    def get_exchange_client(self, exchange_id: ExchangeId) -> ExchangeClient:
        """Get or create exchange client"""
        if not hasattr(self, "_exchange_clients"):
            self._exchange_clients: dict[ExchangeId, ExchangeClient] = {}

        if exchange_id not in self._exchange_clients:
            self._exchange_clients[exchange_id] = ExchangeClient(
                self.settings, exchange_id
            )

        return self._exchange_clients[exchange_id]

    def get_fetch_pairs_command(self, exchange_id: ExchangeId) -> FetchPairsCommand:
        """Get fetch pairs command for specific exchange"""
        exchange_client = self.get_exchange_client(exchange_id)
        return FetchPairsCommand(exchange_client, self.pair_repository, self.settings)

    def get_match_pairs_command(self) -> MatchPairsCommand:
        """Get match pairs command"""
        return MatchPairsCommand(self.pair_matcher, self.pair_repository, self.settings)

    def get_sort_pairs_command(self) -> SortPairsCommand:
        """Get sort pairs command"""
        return SortPairsCommand(
            self.market_sorter,
            self.pair_repository,
            self.market_repository,
            self.settings,
        )
