# Troubleshooting Guide

This guide helps you identify and fix common issues with the Sandwich application.

## Common Issues and Solutions

### 1. Installation Issues

#### Problem: uv command not found

**Solution:**
```bash
# Reinstall uv using official script
curl -LsSf https://astral.sh/uv/install.sh | sh

# Check if uv is in your PATH
echo $PATH
ls -la ~/.local/bin

# If not found, add to PATH (add to .bashrc or .zshrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

#### Problem: Failed to install dependencies with uv sync

**Solution:**
```bash
# Clear uv cache and reinstall
uv cache clean
uv sync

# Try with verbose output
uv sync -v

# Check Python version
python --version
# Should be Python 3.12 or later
```

### 2. Runtime Issues

#### Problem: Exchange not found error

**Error message:** `ValueError: Unknown exchange: <exchange_name>`

**Solution:**
1. Check if the exchange is supported in `ExchangeId` enum (`src/sandwich/domain/models.py`)
2. Verify the exchange is configured in `EXCHANGE_CONFIG` (`src/sandwich/config/exchanges.py`)
3. Check for typos in the exchange name (case-sensitive)

#### Problem: ccxt exchange not available

**Error message:** `AttributeError: module 'ccxt' has no attribute '<exchange_name>'`

**Solution:**
1. Check if the exchange is supported by ccxt library
2. Verify ccxt version: `uv pip list | grep ccxt`
3. Try updating ccxt: `uv pip install -U ccxt`

#### Problem: CoinGecko API rate limit exceeded

**Error message:** `Too many requests or rate limit exceeded`

**Solution:**
1. Wait for the rate limit to reset (usually 1 minute)
2. Reduce the frequency of `--fetch` calls
3. Set environment variable: `export COINGECKO_RATE_LIMIT=30`

#### Problem: Pair matching issues

**Error message:** `No pairs matched between exchanges` or `0 pairs matched with market data`

**Solution:**
1. Check if the exchange is configured with `match_with` parameter
2. Verify the base currency and market type are compatible
3. Check if the exchange has active trading pairs for the specified type
4. Manually verify pairs using exchange's website

### 3. Output Issues

#### Problem: No output file generated

**Solution:**
1. Check if `--get-pairs` flag is included
2. Verify the exchange has active pairs for the specified parameters
3. Check file permissions in the project directory
4. Look for error messages in the console output

#### Problem: Invalid TradingView format

**Solution:**
1. Ensure the output file has valid pair names
2. Check if the file is properly formatted (one pair per line)
3. Verify that symbols match TradingView format (e.g., `BINANCE:BTCUSDT`)

### 4. Performance Issues

#### Problem: Application takes too long to run

**Solution:**
1. Check internet connection speed
2. Reduce frequency of `--fetch` calls
3. Use `--no-fetch` if you don't need updated market data
4. Ensure cache is working correctly (check `.cache/` directory)

#### Problem: Memory usage is high

**Solution:**
1. Close unnecessary applications
2. Limit the number of pairs being processed
3. Use `--no-fetch` to avoid loading large market data
4. Restart the application

### 5. Cache Issues

#### Problem: Stale data in cache

**Solution:**
1. Clear the cache directory:
   ```bash
   rm -rf .cache/
   ```
2. Set shorter cache TTL:
   ```bash
   export SANDWICH_CACHE_TTL=300  # 5 minutes
   ```
3. Run with `--fetch` to get fresh data

#### Problem: Cache directory not writable

**Solution:**
1. Check directory permissions:
   ```bash
   ls -la ~/.cache
   ```
2. Change cache directory location:
   ```bash
   export SANDWICH_CACHE_DIR="/path/to/writable/directory"
   ```

## Debugging Techniques

### 1. Enable Verbose Logging

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uv run sandwich --base usdtperp --fetch --get-pairs
```

### 2. Check Exchange Status

```bash
# Test if exchange is reachable
curl -I https://api.binance.com/api/v3/ping

# Check if exchange API is working
curl -I https://api.coingecko.com/api/v3/ping
```

### 3. Validate Configuration

```bash
# Check Python version
python --version

# Verify dependencies are installed
uv pip list

# Run tests
uv run pytest -v
```

## Getting Help

If you're experiencing an issue not covered here, try:

1. Checking the [GitHub Issues](../../issues) page for similar problems
2. Searching the repository for related error messages
3. Running the tests to identify failing components
4. Providing detailed error messages and steps to reproduce the issue when reporting

## Common Error Codes and Meanings

| Error Code | Meaning | Solution |
|-----------|---------|----------|
| 403 | Forbidden - API key required or IP banned | Check API credentials, verify IP address |
| 429 | Too Many Requests - Rate limit exceeded | Wait, reduce frequency, check API limits |
| 500 | Server Error - Exchange API issue | Retry later, check exchange status page |
| 503 | Service Unavailable | Retry later, check exchange status |
