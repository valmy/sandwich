# Development Guide

This guide is for developers who want to contribute to the Sandwich project.

## Getting Started

### Prerequisites

- Python 3.12 or later
- uv (Python package manager)
- Git

### Development Setup

```bash
# Fork and clone the repository
git clone <your-fork-url>
cd sandwich

# Create a virtual environment
uv venv

# Install dependencies (including dev dependencies)
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

## Project Structure

```
sandwich/
├── src/sandwich/                    # Main application code
│   ├── domain/                      # Domain layer (business logic)
│   │   ├── __init__.py
│   │   ├── exceptions.py           # Custom exceptions
│   │   ├── models.py               # Data models
│   │   ├── services.py             # Domain services
│   │   └── validators.py           # Validation logic
│   ├── application/                # Application layer (use cases)
│   │   ├── __init__.py
│   │   ├── cli.py                  # CLI entry point
│   │   ├── commands.py             # Command implementations
│   │   ├── container.py            # Dependency injection
│   │   └── output.py               # Output formatting
│   ├── infrastructure/             # Infrastructure layer (external APIs)
│   │   ├── __init__.py
│   │   ├── cache.py                # Cache implementation
│   │   ├── filesystem.py           # File system operations
│   │   ├── logging.py              # Logging configuration
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── base.py             # Base API client
│   │       ├── coingecko.py        # CoinGecko API client
│   │       └── exchanges.py        # Exchange API clients (ccxt)
│   ├── repositories/               # Repositories (data access)
│   │   ├── __init__.py
│   │   ├── pair_repository.py      # Trading pair data
│   │   └── market_repository.py    # Market data
│   └── config/
│       ├── __init__.py
│       └── exchanges.py            # Exchange configuration
├── tests/                          # Test files
├── docs/                           # Documentation
└── pyproject.toml                 # Project configuration
```

## Development Workflow

### 1. Create a Branch

```bash
# Create and checkout a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow standard Python coding rules (PEP 8)
- Write clear, concise commit messages
- Add tests for new functionality

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/sandwich tests/

# Run specific test file
uv run pytest tests/test_commands.py -v

# Run specific test function
uv run pytest tests/test_commands.py::test_get_pairs_command -v
```

### 4. Code Quality Checks

```bash
# Run linting with ruff
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix

# Run code formatting with ruff
uv run ruff format .

# Type checking with mypy
uv run mypy .

# Type checking with pyright
uv run pyright .
```

### 5. Build the Package

```bash
# Build the package
uv build

# Test the CLI
uv run sandwich --help
```

## Creating Pull Requests

### 1. Commit Changes

```bash
# Add and commit your changes
git add .
git commit -m "Add feature: your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 2. Create PR

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out the PR template
4. Assign reviewers if needed
5. Submit the PR

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Use `pytest` as the testing framework
- Follow the pattern: `test_<function_name>.py`
- Use fixtures for common setup (see `tests/conftest.py`)
- Mock external API calls

### Test Examples

```python
# tests/test_domain_services.py
def test_process_pairs():
    # Arrange
    pairs = [Pair(symbol="BTCUSDT")]
    market_data = {"BTC": MarketData(market_cap=1000000000000, volume=100000000)}
    
    # Act
    processed = process_pairs(pairs, market_data)
    
    # Assert
    assert len(processed) == 1
    assert processed[0].symbol == "BTCUSDT"
```

## Debugging

### Running in Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG uv run sandwich --base usdtperp --fetch --get-pairs
```

### Using VSCode Debugger

1. Install VSCode Python extension
2. Create a `launch.json` file:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Sandwich CLI",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/src/sandwich/application/cli.py",
               "args": ["--base", "usdtperp", "--fetch", "--get-pairs"],
               "console": "integratedTerminal"
           }
       ]
   }
   ```

## Adding New Features

### Adding Support for a New Exchange

1. Add to `ExchangeId` enum (`src/sandwich/domain/models.py`)
2. Add to `EXCHANGE_CONFIG` (`src/sandwich/config/exchanges.py`)
3. Update documentation in `README.md` and `docs/configuration.md`
4. Write tests for the new exchange

### Adding New Configuration Options

1. Add option to CLI in `src/sandwich/application/cli.py`
2. Handle the option in the command implementation
3. Update documentation in `docs/configuration.md`
4. Write tests for the new option

## Release Process

1. Update version in `pyproject.toml`
2. Create a release branch
3. Run all tests
4. Update documentation
5. Create a tag
6. Publish to package repository

## Contributing Guidelines

1. Follow the code style guidelines
2. Write tests for all new features
3. Keep pull requests focused and minimal
4. Add clear documentation for changes
5. Respect existing code patterns

## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.
