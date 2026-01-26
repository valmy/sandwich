# AGENTS.md

## Build/Lint/Test Commands

1. **Build**: `uv build` - builds the Python package using uv
2. **Run the application**: `uv run sandwich [OPTIONS]` - runs the main application with available options
3. **Run tests**: `uv run pytest` - runs all tests in the project
4. **Run a single test**: `uv run pytest path/to/test_file.py -v` - runs tests from a specific file with verbose output
5. **Run a specific test function**: `uv run pytest path/to/test_file.py::test_function_name -v`
6. **Linting**: `uv run ruff check .` - runs linting checks on the codebase
7. **Auto-fix linting issues**: `uv run ruff check . --fix` - automatically fixes linting issues where possible
8. **Format code**: `uv run ruff format .` - formats code according to project style
9. **Type checking (mypy)**: `uv run mypy .` - runs mypy type checking on the codebase
10. **Type checking (pyright)**: `uv run pyright .` - runs pyright type checking on the codebase
11. **Install dependencies**: `uv sync` - synchronizes dependencies with uv.lock

## Code Style Guidelines

### Formatting
- Follow PEP 8 style guide
- Line length limit: 79 characters
- Use 4 spaces for indentation (no tabs)
- Use blank lines to separate logical sections (2 blank lines between top-level functions)

### Imports
- Standard library imports first (e.g., `import os`, `import json`, `import time`)
- Third-party imports next (e.g., `import requests`, `import ccxt`, `import typer`)
- Local imports last (e.g., `from .coingecko.markets import save_market_data`)
- Use absolute imports rather than relative imports
- Sort imports alphabetically within each group
- One import per line preferred for clarity

### Type Hints
- Use Python 3.12+ type hints
- Include type annotations for all function parameters and return values
- Use `from typing import Any, Dict, List, Optional, Tuple, Union` when needed
- Default values don't require explicit type hints if the type is obvious
- Example: `def get_pairs(base_currency: str = 'USDT', type: str = 'swap'):`

### Naming Conventions
- Use snake_case for functions and variables (e.g., `get_and_save_pairs`, `market_type`)
- Use PascalCase for class names (e.g., `Exchange`, `Pair`)
- Use uppercase with underscores for constants (e.g., `MAX_RETRIES`, `API_URL`)
- Use descriptive names that indicate purpose
- Avoid single-letter variable names except in list comprehensions

### Error Handling
- Use try/except blocks for error handling
- Include specific exception types rather than generic `Exception` when possible
- Print meaningful error messages when exceptions occur
- Return empty lists or None on error when appropriate
- Example:
  ```python
  try:
      exchange = ccxt.hyperliquid()
      markets = exchange.load_markets()
      return markets
  except Exception as e:
      print(f"Error fetching Hyperliquid data via ccxt: {e}")
      return []
  ```

### Documentation
- Write docstrings for all public modules, functions, and classes
- Use Google-style docstring format with Args and Returns sections
- Include parameter descriptions and return type information
- Keep docstrings concise but informative
- Example:
  ```python
  def get_pairs(base_currency: str = 'USDC', type: str = 'swap'):
      """
      Retrieves pairs from Hyperliquid exchange using ccxt.

      Args:
          base_currency (str): The base currency to filter pairs (e.g., 'USDC').
          type (str): The type of pairs to retrieve ('swap' or 'spot').

      Returns:
          list: A list of trading pairs from Hyperliquid.
      """
  ```

### Code Organization
- Keep functions focused on a single responsibility
- Use separate modules for different concerns (binance/, coingecko/, hyperliquid/)
- Group related functions together in the same file
- Use `if __name__ == "__main__":` for script entry points
- Avoid deep nesting (more than 3-4 levels)

### File Structure
- Main entry point: `src/sandwich/__init__.py`
- Exchange-specific modules in subdirectories (binance/, coingecko/, hyperliquid/)
- Processing logic in `process.py`
- Each subdirectory has its own `__init__.py` (can be empty)
- Data files (pairs, market cap) are stored in project root

### API Integration Patterns
- Use ccxt library for exchange interactions (Binance, Hyperliquid)
- Use requests library for HTTP requests (CoinGecko API)
- Implement retry logic for rate-limited APIs (e.g., exponential backoff)
- Handle special cases like coin name prefixes ('k' for Hyperliquid, '1000' for Binance)
- Always check for active markets when filtering pairs

### File I/O
- Use context managers (`with open() as f:`) for file operations
- Specify encoding when appropriate (though defaults work for ASCII)
- Read entire files when small, or use line-by-line iteration for large files
- Print success messages after file operations

### String Handling
- Use f-strings for string formatting (e.g., `f"{exchange_id} pairs: {len(pairs)} found"`)
- Use `.upper()` or `.lower()` for case-insensitive comparisons
- Use `.strip()` to clean user input or file data
- Handle string prefixes/suffixes explicitly (e.g., `BINANCE:`, `PERP`)

### Testing
- Write tests in `test_*.py` or `*_test.py` files
- Use pytest as the test framework
- Follow naming convention: `test_<function_name>` for test functions
- Mock external API calls in tests (requests, ccxt)
- Test both success and error cases

### Function Design
- Use default arguments for common use cases (e.g., `base_currency='USDT'`)
- Return data structures that can be chained (e.g., return lists for further processing)
- Use helper functions to break down complex logic
- Print progress messages for long-running operations
- Example: `print(f"Getting {base_currency} {type} pairs...")`

### Dictionary and List Operations
- Use list comprehensions for filtering and transformation
- Use dictionary lookups with `.get()` for safe access
- Sort using `sorted()` with `key` parameter for custom ordering
- Example: `pairs = [s for s, m in markets.items() if m['active'] and m['quote'] == currency]`

### File Naming Conventions
- Pair files: `{base_currency.lower()}_{market_type}_pairs.txt`
- Sorted files: `sorted_{base_currency.lower()}_{market_type}.txt`
- Hyperliquid pairs: `{base_currency.lower()}_{market_type}_hype_pairs.txt`
- Example: `usdt_swap_pairs.txt`, `sorted_usdc_spot.txt`

## Existing AI Tools Configuration
1. **Cursor**: Follow standard Python coding rules
2. **Copilot**: Follow standard Python coding rules
3. **Sourcegraph Cody**: Follow standard Python coding rules

## Project Context
This is a Python CLI application that fetches and maintains TradingView-compatible trading pair lists from cryptocurrency exchanges. It supports multiple exchanges (Binance, Hyperliquid, Aster, and other ccxt-supported exchanges), integrates with CoinGecko for volume data, and allows sorting pairs by market metrics. The application uses uv for dependency management and supports different base currencies (USDT, USDC, FDUSD) and market types (spot, swap/perpetual).

## Exchange Configuration

Exchanges are configured in `src/sandwich/config/exchanges.py`. Each exchange has:
- `quote`: Default quote currency (e.g., "USDT", "USDC")
- `match_with` (optional): Exchange to match pairs against (e.g., "binance")

Exchanges with `match_with` will have their pairs filtered against the specified exchange.

### Adding a New Exchange

1. Add the exchange to `ExchangeId` enum in `src/sandwich/domain/models.py`
2. Add configuration to `EXCHANGE_CONFIG` in `src/sandwich/config/exchanges.py`:
   ```python
   "new_exchange": {
       "quote": "USDT",
       "match_with": "binance",  # Optional
   },
   ```

## CLI Usage

```bash
# Fetch and get pairs from specific exchange
uv run sandwich --base usdtperp --get-pairs --exchange binance

# Fetch and get pairs from Hyperliquid (with matching against Binance)
uv run sandwich --base usdcperp --get-pairs --exchange hyperliquid

# Sort existing pairs by volume
uv run sandwich --base usdtperp

# Fetch market data from CoinGecko
uv run sandwich --fetch
```
