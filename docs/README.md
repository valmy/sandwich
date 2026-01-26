# Sandwich Documentation

This is the comprehensive documentation for the Sandwich application.

## Table of Contents

- [Quick Start Guide](quick-start.md) - Get up and running in minutes
- [Usage Guide](usage.md) - Detailed usage examples for all commands
- [Configuration Guide](configuration.md) - Customization options
- [Troubleshooting Guide](troubleshooting.md) - Fix common issues
- [Development Guide](development.md) - Contribution guidelines

## About Sandwich

Sandwich is a Python CLI application that fetches and maintains TradingView-compatible trading pair lists from cryptocurrency exchanges. It supports multiple exchanges, integrates with CoinGecko for volume data, and allows sorting pairs by market metrics.

### Key Features

- **Multiple Exchanges Support**: Binance, Hyperliquid, Aster, Bybit, OKX, KuCoin, Gate.io, and other ccxt-supported exchanges
- **Trading Pair Management**: Fetch and maintain spot and perpetual (swap) trading pairs
- **Market Data Integration**: CoinGecko API integration for volume and market cap data
- **Smart Filtering**: Match pairs across exchanges (e.g., Hyperliquid pairs against Binance)
- **TradingView Compatibility**: Generate properly formatted lists for TradingView watchlists
- **CLI Interface**: Easy-to-use command-line interface with intuitive options
- **Configurable**: Support for different base currencies (USDT, USDC, FDUSD) and market types
- **Efficient Caching**: Local caching of exchange and market data to reduce API calls
- **Structured Output**: Support for text and JSON output formats

## Getting Help

If you need help with the application, check the:
1. [Quick Start Guide](quick-start.md) for initial setup
2. [Usage Guide](usage.md) for detailed examples
3. [Troubleshooting Guide](troubleshooting.md) for common issues
4. [Development Guide](development.md) for contributing to the project

## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.
