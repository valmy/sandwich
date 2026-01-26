# Configuration Guide

This guide explains how to configure and customize the Sandwich application.

## Configuration Options

### Command-line Configuration

The main way to configure Sandwich is through command-line arguments. Here are the available options:

#### Base Currency and Market Type

The `--base` option specifies both the base currency and market type:

```bash
# USDT perpetual futures (default)
uv run sandwich --base usdtperp

# USDC spot
uv run sandwich --base usdc

# FDUSD perpetual futures
uv run sandwich --base fdusdperp
```

**Format:** `<currency_code>[perp]`
- Without `perp`: Spot market
- With `perp`: Perpetual futures (swap) market

#### Exchange Configuration

The `--exchange` option specifies which exchange to use:

```bash
uv run sandwich --exchange binance
uv run sandwich --exchange hyperliquid
uv run sandwich --exchange aster
```

Available exchanges: binance, hyperliquid, aster, bybit, okx, kucoin, gateio

#### Output Format

The `--output` option controls the output format:

```bash
# Text format (default)
uv run sandwich --output text

# JSON format
uv run sandwich --output json
```

### File-based Configuration

Exchange-specific configuration is stored in `src/sandwich/config/exchanges.py`:

```python
EXCHANGE_CONFIG: dict[str, ExchangeConfig] = {
    "binance": {
        "quote": "USDT",
    },
    "hyperliquid": {
        "quote": "USDC",
        "match_with": "binance",
    },
    "aster": {
        "quote": "USDC",
        "match_with": "binance",
    },
    "bybit": {
        "quote": "USDT",
        "match_with": "binance",
    },
}
```

Each exchange configuration supports:
- `quote`: Default quote currency for the exchange
- `match_with` (optional): Exchange to match pairs against

### Adding a New Exchange

1. Add the exchange to `ExchangeId` enum in `src/sandwich/domain/models.py`:
   ```python
   class ExchangeId(StrEnum):
       BINANCE = "binance"
       HYPERLIQUID = "hyperliquid"
       ASTER = "aster"
       NEW_EXCHANGE = "new_exchange"
   ```

2. Add configuration to `EXCHANGE_CONFIG` in `src/sandwich/config/exchanges.py`:
   ```python
   "new_exchange": {
       "quote": "USDT",
       "match_with": "binance",  # Optional: Match against another exchange's pairs
   },
   ```

### Environment Variables

Sandwich supports the following environment variables:

#### Cache Configuration

```bash
# Set cache directory (default: .cache)
export SANDWICH_CACHE_DIR="/path/to/cache"

# Set cache TTL in seconds (default: 3600 - 1 hour)
export SANDWICH_CACHE_TTL=86400
```

#### CoinGecko API Configuration

```bash
# Set CoinGecko API rate limit (requests per minute)
export COINGECKO_RATE_LIMIT=50

# Set CoinGecko API timeout in seconds
export COINGECKO_TIMEOUT=30
```

### File Storage

Sandwich stores data in the following files:

| File | Purpose |
|------|---------|
| `coingecko_data.json` | Market data from CoinGecko (cached) |
| `<currency>_<type>_pairs.txt` | Raw pairs from exchanges |
| `sorted_<currency>_<type>.txt` | Sorted pairs with metrics |
| `<currency>_<type>_<exchange>_pairs.txt` | Exchange-specific pairs |

## Advanced Configuration

### Custom Output Formats

You can add custom output formats by extending the `OutputFormatter` class in `src/sandwich/application/output.py`.

### Custom Exchange Integrations

For advanced use cases, you can create custom exchange integrations by:
1. Creating a new exchange class in `src/sandwich/infrastructure/api/exchanges.py`
2. Implementing the required methods for fetching and processing pairs
3. Adding the exchange to the configuration

## Configuration Best Practices

1. Use command-line arguments for most configuration needs
2. Modify the `EXCHANGE_CONFIG` for permanent exchange configuration
3. Use environment variables for sensitive or dynamic configuration
4. Regularly check for updates to exchange configurations
