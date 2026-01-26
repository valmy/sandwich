# Sandwich - TradingView Compatible Cryptocurrency Pair List Manager

## Project Overview

Sandwich is a Python CLI application that fetches and maintains TradingView-compatible trading pair lists from cryptocurrency exchanges. It supports multiple exchanges, integrates with CoinGecko for volume data, and allows sorting pairs by market metrics. The application uses modern Python practices and dependency management with uv.

## Key Features

- **Multiple Exchanges Support**: Binance, Hyperliquid, Aster, Bybit, OKX, KuCoin, Gate.io, and other ccxt-supported exchanges
- **Trading Pair Management**: Fetch and maintain spot and perpetual (swap) trading pairs
- **Market Data Integration**: CoinGecko API integration for volume and market cap data
- **Smart Filtering**: Match pairs across exchanges (e.g., Hyperliquid pairs against Binance)
- **TradingView Compatibility**: Generate properly formatted lists for TradingView watchlists
- **CLI Interface**: Easy-to-use command-line interface with intuitive options
- **Configurable**: Support for different base currencies (USDT, USDC, FDUSD) and market types
- **Efficient Caching**: Local caching of exchange and market data to reduce API calls
- **Structured Output**: Support for text and JSON output formats

## Architecture Overview

The application follows a clean architecture pattern with distinct layers:

### Domain Layer (`src/sandwich/domain/`)
- Core business logic and entity definitions
- `models.py`: Data models including `Pair`, `MarketData`, and `ExchangeId` enum
- `services.py`: Domain services for processing pairs and market data
- `validators.py`: Validation logic for inputs and data structures

### Application Layer (`src/sandwich/application/`)
- Use case orchestration and CLI interface
- `cli.py`: Main entry point with Typer-based CLI commands
- `commands.py`: Command implementations for fetching, processing, and sorting pairs
- `container.py`: Dependency injection container for managing dependencies

### Infrastructure Layer (`src/sandwich/infrastructure/`)
- External API and file system interactions
- `filesystem.py`: File system operations for reading/writing pair lists
- `api/exchanges.py`: ccxt integration for exchange interactions
- `api/coingecko.py`: CoinGecko API client for market data

### Repositories (`src/sandwich/repositories/`)
- Data access abstractions
- `pair_repository.py`: Repository for managing trading pair data
- `market_repository.py`: Repository for managing market data

### Configuration (`src/sandwich/config/`)
- `exchanges.py`: Exchange-specific configuration and settings

## Installation

### Prerequisites

- Python 3.12 or later
- uv (Python package manager)

### Install uv

```bash
# Using official installation script
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Clone and Set Up the Project

```bash
# Clone the repository
git clone <repository-url>
cd sandwich

# Install dependencies
uv sync
```

## Usage

### CLI Options

```bash
uv run sandwich [OPTIONS]
```

**Core Options:**
- `--base TEXT`: Base currency and market type combined. For swap/perpetual markets, append 'perp' to the base currency. For spot markets, use just the currency code. [default: usdtperp]
  - Examples:
    - 'usdtperp' = USDT base currency, swap/perpetual market
    - 'usdc' = USDC base currency, spot market
    - 'fdusdperp' = FDUSD base currency, swap/perpetual market

- `--fetch/--no-fetch`: Fetch latest market data (price, volume, market cap) from CoinGecko API. This data is used for sorting pairs by metrics like market cap or volume. [default: no-fetch]

- `--get-pairs/--no-get-pairs`: Fetch and update trading pairs from the specified exchange. Pairs are filtered by the base currency and market type, and only active markets are included. [default: no-get-pairs]

- `--exchange, -e`: Exchange to use for fetching pairs. [default: binance]
  - Supported exchanges: binance, hyperliquid, aster, bybit, okx, kucoin, gateio
  - Note: Exchanges with 'match_with' configuration will filter pairs against the specified exchange's pairs.

- `--output, -o`: Output format. Supported formats: text, json [default: text]

### Common Usage Examples

#### 1. Fetch and Process Binance USDC Spot Pairs

```bash
uv run sandwich --base usdc --fetch --get-pairs
```

#### 2. Fetch and Process Hyperliquid USDC Perpetual Pairs

```bash
uv run sandwich --base usdcperp --fetch --get-pairs --exchange hyperliquid
```

#### 3. Only Sort Existing Pairs

```bash
uv run sandwich --base usdtperp
```

#### 4. Get Help

```bash
uv run sandwich --help
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Quick Start Guide](docs/quick-start.md) - Get up and running in minutes
- [Usage Guide](docs/usage.md) - Detailed usage examples for all commands
- [Configuration Guide](docs/configuration.md) - Customization options
- [Troubleshooting Guide](docs/troubleshooting.md) - Fix common issues
- [Development Guide](docs/development.md) - Contribution guidelines

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Configuration

### Exchange Configuration

Exchanges are configured in `src/sandwich/config/exchanges.py`. Each exchange has:
- `quote`: Default quote currency (e.g., "USDT", "USDC")
- `match_with` (optional): Exchange to match pairs against (e.g., "binance")

Example configuration:
```python
"hyperliquid": {
    "quote": "USDC",
    "match_with": "binance",
},
"aster": {
    "quote": "USDC",
    "match_with": "binance",
},
```

### Adding a New Exchange

1. Add the exchange to `ExchangeId` enum in `src/sandwich/domain/models.py`
2. Add configuration to `EXCHANGE_CONFIG` in `src/sandwich/config/exchanges.py`:

```python
"new_exchange": {
    "quote": "USDT",
    "match_with": "binance",  # Optional
},
```

### Environment Variables

All settings can be configured using environment variables with the `SANDWICH_` prefix. Settings are case-insensitive.

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `SANDWICH_DATA_DIR` | Data directory for storing pair files and market data | Current working directory |
| `SANDWICH_MARKETCAP_FILE` | Filename for market data cache | `marketcap.json` |
| `SANDWICH_COINGECKO_API_URL` | CoinGecko API base URL | `https://api.coingecko.com/api/v3/coins/markets` |
| `SANDWICH_MAX_RETRIES` | Maximum number of API retry attempts | 5 |
| `SANDWICH_ITEMS_PER_PAGE` | Number of items per API page | 250 |
| `SANDWICH_PAGES_TO_FETCH` | Number of pages to fetch from CoinGecko | 2 |
| `SANDWICH_BASE_CURRENCY` | Default base currency for pairs | `USDT` |
| `SANDWICH_STABLECOINS_FILE` | Filename for stablecoins cache | `stablecoins.json` |

Example usage:
```bash
SANDWICH_DATA_DIR=/data SANDWICH_MAX_RETRIES=3 uv run sandwich --base usdtperp --fetch
```

## File Structure

```
sandwich/
├── src/sandwich/
│   ├── application/         # CLI and use case orchestration
│   ├── config/             # Configuration files
│   ├── domain/             # Core business logic and models
│   ├── infrastructure/     # External API and file system interactions
│   └── repositories/       # Data access abstractions
├── tests/                  # Test files and fixtures
├── README.md              # Documentation
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Dependency lock file
└── [pair files]           # Generated trading pair lists (e.g., usdt_swap_pairs.txt)
```

## Troubleshooting

### Common Issues

1. **Exchange Connection Errors**:
   - Check internet connectivity
   - Verify exchange API status (e.g., Binance API status page)
   - Ensure exchange supports the requested market type

2. **Missing Pairs**:
   - Check if the base currency is supported by the exchange
   - Verify market type (spot vs. swap)
   - For matched pairs, ensure the reference exchange has the pair

3. **CoinGecko API Rate Limiting**:
   - The application implements rate limiting
   - If errors persist, wait a few minutes before retrying
   - Consider adding API key support (future feature)

4. **File Write Errors**:
   - Ensure you have write permissions to the project directory
   - Check disk space
   - Verify file paths are accessible

### Debugging

Enable debug logging by setting the `LOG_LEVEL` environment variable:

```bash
LOG_LEVEL=DEBUG uv run sandwich --base usdtperp --get-pairs
```

## Testing

Run the test suite using pytest:

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/sandwich

# Run specific test file
uv run pytest tests/test_domain_services.py -v

# Run specific test function
uv run pytest tests/test_domain_services.py::test_process_and_sort_pairs -v
```

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests and linting:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run ruff format .
   ```
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write meaningful commit messages
- Add tests for new functionality
- Update documentation for changes
- Use type hints with Python 3.12+ syntax

### AI Tools Usage

This project uses AI tools for development:
- **Github Copilot**: AI pair programming
- **Cursor AI**: Enhanced code editing with AI
- **Sourcegraph Cody**: Codebase exploration and understanding

## License

[Add your license information here]

## Authors

- T. Budiman - Initial development

## Acknowledgments

- [ccxt](https://github.com/ccxt/ccxt) - Cryptocurrency exchange integration library
- [CoinGecko](https://www.coingecko.com/) - Cryptocurrency market data API
- [TradingView](https://www.tradingview.com/) - Charting and analysis platform

## Changelog

### v0.2.0
- Added support for multiple exchanges (Binance, Hyperliquid, Aster)
- Improved architecture with clean layers
- Enhanced CLI interface
- Added market data integration
- Support for matched pairs across exchanges

### v0.1.0
- Initial version
- Basic Binance pair management
- CoinGecko integration
- TradingView compatible output
