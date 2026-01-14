# Unit Testing Plan for Sandwich CLI

## Overview
This document outlines the comprehensive unit testing strategy for the Sandwich CLI application.

## Testing Philosophy
- **Test Pyramid**: ~70% unit tests, ~20% integration tests, ~10% end-to-end tests
- **Isolation**: Each test should be independent and not rely on other tests
- **Mocking**: All external dependencies (APIs, file I/O) should be mocked
- **Coverage Goal**: Aim for 80%+ code coverage across all modules

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_binance.py                # Binance module tests
├── test_coingecko.py              # CoinGecko module tests
├── test_hyperliquid.py            # Hyperliquid module tests
├── test_process.py                # Process/Sorting module tests
├── test_main.py                   # Main CLI integration tests
├── fixtures/                      # Test fixtures
│   ├── __init__.py
│   ├── binance_fixtures.py
│   ├── coingecko_fixtures.py
│   └── hyperliquid_fixtures.py
└── utils/                         # Test utilities
    ├── __init__.py
    └── helpers.py
```

## Dependencies to Add
```toml
[dependency-groups]
dev = [
    "mypy>=1.19.1",
    "pyright>=1.1.408",
    "ruff>=0.14.11",
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.12.0",
    "pytest-asyncio>=0.23.0",
]
```

---

## Test Coverage by Module

### 1. `src/sandwich/coingecko/markets.py`

#### Functions to Test:
- `make_request(url, max_retries=5)`
- `download_file(url, file_path)`
- `save_market_data(file_name='marketcap.json')`

#### Test Cases:
**`make_request`**
- ✓ Successful request (status 200)
- ✓ Rate limit handling (429 status, exponential backoff)
- ✓ Max retries exhausted
- ✓ Network errors handled
- ✓ Invalid URL

**`download_file`**
- ✓ Successful download and file write
- ✓ HTTP 404 error handling
- ✓ Permission denied on file write
- ✓ Invalid file path
- ✓ Binary data preservation

**`save_market_data`**
- ✓ Single page fetch success
- ✓ Multiple pages fetch success (2 pages, 500 items)
- ✓ Empty response handling
- ✓ Malformed JSON handling
- ✓ File write success
- ✓ File write error handling
- ✓ Network error recovery

**Fixtures Needed:**
- Mock requests response with market data
- Mock 429 rate limit response
- Mock error responses
- Temporary file fixture for file I/O tests

---

### 2. `src/sandwich/binance/pairs.py`

#### Functions to Test:
- `get_pairs(base_currency='USDT', type='swap')`
- `save_pairs_for_tradingview(pairs, base_currency, type, filename=None)`
- `get_and_save_pairs(base_currency='USDT', type='swap')`

#### Test Cases:
**`get_pairs`**
- ✓ USDT swap pairs retrieval
- ✓ USDC spot pairs retrieval
- ✓ FDUSD swap pairs retrieval
- ✓ Empty result handling (no active pairs)
- ✓ Invalid base currency
- ✓ Invalid market type
- ✓ API error handling

**`save_pairs_for_tradingview`**
- ✓ Swap pairs format (PERP suffix)
- ✓ Spot pairs format (no suffix)
- ✓ Custom filename
- ✓ Default filename generation
- ✓ Empty pairs list
- ✓ File write error handling
- ✓ TradingView format correctness
- ✓ BINANCE: prefix inclusion

**`get_and_save_pairs`**
- ✓ End-to-end flow (fetch + save)
- ✓ Print output verification
- ✓ Error propagation

**Fixtures Needed:**
- Mock ccxt.binance() exchange
- Mock market data with active/inactive pairs
- Mock markets with different quote currencies
- Mock markets with swap/spot types
- Temporary file fixture

---

### 3. `src/sandwich/hyperliquid/pairs.py`

#### Functions to Test:
- `get_pairs(base_currency='USDC', type='swap')`
- `normalize_coin_name(coin)`
- `load_pairs_from_file(base_currency='USDT', type='swap')`
- `get_ccxt_pairs(exchange_id, base_currency, type)`
- `match_with_binance_pairs(hyperliquid_pairs, binance_base_currency, type)`
- `match_pairs_between_exchanges(...)`
- `save_hyperliquid_pairs_for_tradingview(...)`
- `save_pairs_for_tradingview(...)`
- `get_and_save_hyperliquid_pairs(...)`
- `get_and_save_ccxt_pairs(...)`

#### Test Cases:
**`get_pairs`**
- ✓ USDC swap pairs retrieval
- ✓ USDC spot pairs retrieval
- ✓ API error handling
- ✓ Empty result handling

**`normalize_coin_name`**
- ✓ 'k' prefix removal (kPEPE -> PEPE)
- ✓ '1000' prefix removal (1000PEPE -> PEPE)
- ✓ Mixed case handling (Kpepe -> pepe)
- ✓ No prefix coin (BTC -> BTC)
- ✓ Single character with 'k' prefix
- ✓ 'k' not followed by uppercase (keep as-is)

**`load_pairs_from_file`**
- ✓ File exists and loads correctly
- ✓ File doesn't exist (warning + empty list)
- ✓ PERP suffix removal for swap
- ✓ No suffix for spot
- ✓ BINANCE: prefix removal
- ✓ CCXT format conversion
- ✓ Base currency location detection

**`get_ccxt_pairs`**
- ✓ Binance pairs retrieval
- ✓ Bybit/OKX pairs retrieval
- ✓ Invalid exchange ID
- ✓ API error handling

**`match_with_binance_pairs`**
- ✓ Exact matches found
- ✓ Special prefix matches (kPEPE -> 1000PEPE)
- ✓ No matches (all missing)
- ✓ Partial matches (some found, some missing)
- ✓ File loading fallback
- ✓ API fallback when file doesn't exist
- ✓ Print output verification
- ✓ Count verification (normal vs special)

**`match_pairs_between_exchanges`**
- ✓ Source: Hyperliquid, Target: Binance
- ✓ Source: Bybit, Target: Binance
- ✓ Different base currencies
- ✓ File vs API fallback logic
- ✓ Missing pairs reporting

**`save_hyperliquid_pairs_for_tradingview`**
- ✓ Correct filename generation
- ✓ PERP suffix for swap
- ✓ No suffix for spot
- ✓ BINANCE: prefix
- ✓ File write success

**`get_and_save_hyperliquid_pairs`**
- ✓ Complete flow: fetch -> match -> save
- ✓ Error propagation
- ✓ Print output verification

**`get_and_save_ccxt_pairs`**
- ✓ No Binance filter (exchange == binance)
- ✓ With Binance filter (exchange != binance, use_existing_binance=True)
- ✓ With Binance filter but use_existing_binance=False
- ✓ File loading vs API fallback
- ✓ Missing pairs reporting
- ✓ Filtered pairs result

**Fixtures Needed:**
- Mock ccxt.hyperliquid() exchange
- Mock ccxt.binance() exchange
- Mock file with Binance pairs
- Mock hyperliquid pairs list
- Mock special prefix pairs (kPEPE, 1000PEPE)
- Temporary file fixtures

---

### 4. `src/sandwich/process.py`

#### Functions to Test:
- `remove_prefix_suffix(s)`
- `find_symbol_in_lines(item, lines, base_currency='USDT')`
- `sort_market_data(base_currency, market_type, is_hyperliquid=False)`

#### Test Cases:
**`remove_prefix_suffix`**
- ✓ Remove BINANCE: prefix
- ✓ Remove PERP suffix
- ✓ Remove both prefix and suffix
- ✓ No prefix/suffix (returns as-is)
- ✓ Multiple BINANCE: occurrences (only removes first)
- ✓ PERP in middle of string (no removal)

**`find_symbol_in_lines`**
- ✓ Exact symbol match found
- ✓ 1000 prefix match (symbol vs 1000symbol)
- ✓ Excluded currencies not matched (USDC, FDUSD, EUR)
- ✓ Symbol not found (returns empty string)
- ✓ Multiple matches (returns first)
- ✓ Case insensitive matching
- ✓ Base currency variations (USDT, USDC)

**`sort_market_data`**
- ✓ Regular pairs sorting (not hyperliquid)
- ✓ Hyperliquid pairs sorting
- ✓ Volume descending order
- ✓ Unsorted symbols appended at end
- ✓ All symbols sorted (0 unsorted)
- ✓ All symbols unsorted (0 sorted)
- ✓ File doesn't exist (marketcap.json)
- ✓ File doesn't exist (pairs txt file)
- ✓ Malformed JSON in marketcap.json
- ✓ Empty market data
- ✓ Empty pairs list
- ✓ Correct filename generation (4 cases)
- ✓ File write success
- ✓ Correct count reporting
- ✓ Integration with find_symbol_in_lines

**Fixtures Needed:**
- Mock market data with volume and market cap
- Mock pairs list (unsorted)
- Mock sorted pairs list (expected output)
- Mock files with TradingView format
- Empty file fixtures
- Malformed JSON fixture
- Temporary file fixtures

---

### 5. `src/sandwich/__init__.py` (CLI Main)

#### Functions to Test:
- `main(base='usdtperp', fetch=False, get_pairs=False, hyperliquid=False)`

#### Test Cases:
- ✓ Default parameters (usdtperp, all flags False)
- ✓ Perp suffix parsing (usdtperp -> USDT, swap)
- ✓ No perp suffix (usdc -> USDC, spot)
- ✓ Fetch flag only (calls save_market_data)
- ✓ Get pairs only (calls get_and_save_pairs)
- ✓ Hyperliquid flag (calls get_and_save_hyperliquid_pairs + sort)
- ✓ Fetch + get pairs (both called)
- ✓ Fetch + hyperliquid (fetch + hyperliquid functions called)
- ✓ Get pairs + hyperliquid (both sorts called)
- ✓ All flags True (all functions called)
- ✓ Mixed case base currency
- ✓ Invalid base currency handling
- ✓ Print output verification

**Fixtures Needed:**
- Mock save_market_data
- Mock get_and_save_pairs
- Mock get_and_save_hyperliquid_pairs
- Mock sort_market_data
- Typer testing utilities

---

## Fixtures Strategy

### `tests/conftest.py`
```python
# Shared fixtures
- pytest_configure(): Add custom markers
- tmp_path: Temporary directory for file operations
- mock_ccxt_exchange: Generic ccxt exchange mock
- mock_requests_response: Mock HTTP response
- sample_market_data: Realistic market data JSON
- sample_binance_pairs: Realistic Binance pairs list
- sample_hyperliquid_pairs: Realistic Hyperliquid pairs list
- sample_tradingview_pairs: TradingView format strings
```

### `tests/fixtures/binance_fixtures.py`
```python
- binance_markets_swap: Mock swap markets
- binance_markets_spot: Mock spot markets
- binance_empty_markets: Empty markets
- binance_error_response: Error scenario
```

### `tests/fixtures/coingecko_fixtures.py`
```python
- coingecko_market_data: Real market data
- coingecko_empty_response: Empty response
- coingecko_rate_limit: 429 response
- coingecko_error: 500 response
```

### `tests/fixtures/hyperliquid_fixtures.py`
```python
- hyperliquid_pairs_usdc: USDC pairs
- hyperliquid_special_prefix: kPEPE, kSHIB, etc.
- hyperliquid_binance_matches: Matching pairs
- hyperliquid_no_matches: No matching pairs
```

---

## Mocking Strategy

### External Dependencies
1. **ccxt library**
   - Mock `ccxt.binance()` and `ccxt.hyperliquid()`
   - Mock `exchange.load_markets()`
   - Return pre-defined market structures

2. **requests library**
   - Mock `requests.get()`
   - Use `pytest-mock` for flexible mocking
   - Test different response codes (200, 429, 404, 500)

3. **File I/O**
   - Use `tmp_path` fixture for temporary files
   - Mock `open()` for error scenarios
   - Test file read/write operations

4. **CLI**
   - Use `typer.testing.CliRunner` for CLI testing
   - Capture stdout for verification
   - Test error exit codes

---

## Integration Tests

### End-to-End Workflows
1. **Full Fetch Workflow**
   - Fetch market data → Get pairs → Sort → Verify output files

2. **Hyperliquid Workflow**
   - Fetch HL pairs → Match with Binance → Sort → Verify output

3. **Multi-Exchange Workflow**
   - Get pairs from multiple exchanges → Match → Compare

### File-Based Integration
- Verify output file formats match TradingView specifications
- Verify sorting order in output files
- Verify filename conventions

---

## Test Organization Principles

### Naming Conventions
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>` (if using classes)
- Test functions: `test_<function_name>_<scenario>`

### Test Markers
```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.slow           # Slow tests (network I/O)
@pytest.mark.external       # Tests hitting external APIs (if any)
```

### Run Commands
```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# With coverage
pytest --cov=src/sandwich --cov-report=html

# Specific test file
pytest tests/test_binance.py

# Specific test function
pytest tests/test_binance.py::test_get_pairs_usdt_swap

# Verbose output
pytest -v
```

---

## Code Coverage Goals

### Target Coverage by Module
- `coingecko/markets.py`: 85%
- `binance/pairs.py`: 90%
- `hyperliquid/pairs.py`: 80% (complex logic)
- `process.py`: 90%
- `__init__.py`: 85%

### Overall Target: 85%+ coverage

---

## Implementation Priority

### Phase 1: Foundation (Week 1)
1. Set up test infrastructure
2. Create `tests/` directory structure
3. Add pytest to dependencies
4. Create `conftest.py` with basic fixtures
5. Create fixture files with sample data

### Phase 2: Core Modules (Week 2)
1. Write tests for `binance/pairs.py`
2. Write tests for `coingecko/markets.py`
3. Write tests for `process.py`

### Phase 3: Complex Logic (Week 3)
1. Write tests for `hyperliquid/pairs.py`
2. Integration tests
3. CLI tests

### Phase 4: Refinement (Week 4)
1. Coverage analysis and gap filling
2. Performance testing (if needed)
3. Documentation of test suite

---

## Success Criteria

- ✓ All unit tests pass
- ✓ 85%+ code coverage
- ✓ CI/CD integration (if applicable)
- ✓ Tests run in < 10 seconds
- ✓ No external API calls in unit tests
- ✓ Mock coverage for all external dependencies
- ✓ Documentation for complex tests

---

## Continuous Integration

### GitHub Actions (example)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: uv sync
      - run: pytest --cov=src/sandwich --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Maintenance

### Keeping Tests Up-to-Date
- Add tests for all new functions
- Update tests when refactoring
- Review coverage weekly
- Update fixtures when API responses change

### Test Documentation
- Docstrings for complex tests
- Comments explaining "why" not "what"
- README in tests/ directory explaining structure
