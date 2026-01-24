# Quick Start Guide

This guide will help you get up and running with Sandwich quickly.

## Prerequisites

- Python 3.12 or later
- uv (Python package manager) - [Installation instructions](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

### Step 1: Install uv

```bash
# Using official installation script
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Step 2: Clone and Set Up the Project

```bash
# Clone the repository
git clone <repository-url>
cd sandwich

# Install dependencies
uv sync
```

## First Run

### 1. Fetch and Process Binance USDT Perpetual Pairs

```bash
uv run sandwich --base usdtperp --fetch --get-pairs
```

This will:
1. Fetch market data from CoinGecko
2. Fetch active trading pairs from Binance
3. Process and sort the pairs by market metrics
4. Generate TradingView-compatible list

### 2. Verify the Output

You should see output like this:
```
Fetching market data from CoinGecko...
Market data saved to coingecko_data.json
Fetching pairs from binance...
Found 156 USDT swap pairs
Pairs saved to usdt_swap_pairs.txt
Processing pairs...
128 pairs matched with market data
Sorted pairs saved to sorted_usdt_swap.txt
```

## Common Commands

### Fetch and Process Binance USDC Spot Pairs

```bash
uv run sandwich --base usdc --fetch --get-pairs
```

### Fetch and Process Hyperliquid USDC Perpetual Pairs

```bash
uv run sandwich --base usdcperp --fetch --get-pairs --exchange hyperliquid
```

### Only Sort Existing Pairs

```bash
uv run sandwich --base usdtperp
```

### Get Help

```bash
uv run sandwich --help
```

## Next Steps

- [Configuration Guide](configuration.md) - Learn how to customize the application
- [Usage Examples](usage.md) - See more detailed usage examples
- [Troubleshooting Guide](troubleshooting.md) - Fix common issues
