# Usage Guide

This guide provides detailed usage examples for all features of the Sandwich application.

## Basic Usage

### Fetch and Process Pairs

```bash
# Fetch and process Binance USDT perpetual pairs (default)
uv run sandwich --base usdtperp --fetch --get-pairs

# Fetch and process Binance USDC spot pairs
uv run sandwich --base usdc --fetch --get-pairs

# Fetch and process Hyperliquid USDC perpetual pairs
uv run sandwich --base usdcperp --fetch --get-pairs --exchange hyperliquid
```

### Only Sort Existing Pairs

```bash
# Sort existing USDT perpetual pairs
uv run sandwich --base usdtperp

# Sort existing USDC spot pairs
uv run sandwich --base usdc
```

### Only Fetch Market Data

```bash
# Fetch CoinGecko market data
uv run sandwich --fetch
```

### Only Fetch Pairs

```bash
# Fetch Binance USDT perpetual pairs without market data
uv run sandwich --base usdtperp --get-pairs
```

## Advanced Usage

### Specify Output Format

```bash
# Text format (default)
uv run sandwich --base usdtperp --fetch --get-pairs --output text

# JSON format
uv run sandwich --base usdtperp --fetch --get-pairs --output json
```

### Custom Exchange Configuration

```bash
# Fetch Bybit USDT perpetual pairs
uv run sandwich --base usdtperp --fetch --get-pairs --exchange bybit

# Fetch OKX USDT perpetual pairs
uv run sandwich --base usdtperp --fetch --get-pairs --exchange okx

# Fetch KuCoin USDT perpetual pairs
uv run sandwich --base usdtperp --fetch --get-pairs --exchange kucoin

# Fetch Gate.io USDT perpetual pairs
uv run sandwich --base usdtperp --fetch --get-pairs --exchange gateio
```

### Different Base Currencies

```bash
# FDUSD spot
uv run sandwich --base fdusd --fetch --get-pairs

# FDUSD perpetual
uv run sandwich --base fdusdperp --fetch --get-pairs
```

### All-in-One Command

```bash
# Fetch data and pairs for all supported base currencies
uv run sandwich --base usdtperp --fetch --get-pairs && \
uv run sandwich --base usdc --fetch --get-pairs && \
uv run sandwich --base fdusdperp --fetch --get-pairs
```

## Scripting and Automation

### Create a Bash Script

```bash
#!/bin/bash

# script.sh - Fetch and process pairs daily

BASE_CURRENCIES=("usdtperp" "usdc" "fdusdperp")
EXCHANGES=("binance" "hyperliquid" "bybit" "okx")

for base in "${BASE_CURRENCIES[@]}"; do
    for exchange in "${EXCHANGES[@]}"; do
        echo "Processing $base on $exchange..."
        uv run sandwich --base "$base" --fetch --get-pairs --exchange "$exchange"
    done
done

echo "All pairs processed successfully!"
```

Make it executable:
```bash
chmod +x script.sh
./script.sh
```

### Schedule with Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily at 08:00 AM
0 8 * * * cd /path/to/sandwich && ./script.sh >> cron.log 2>&1
```

## Understanding the Output

### File Outputs

| File | Purpose |
|------|---------|
| `coingecko_data.json` | Market data from CoinGecko (cached) |
| `<currency>_<type>_pairs.txt` | Raw pairs from exchanges |
| `sorted_<currency>_<type>.txt` | Sorted pairs with metrics |
| `<currency>_<type>_<exchange>_pairs.txt` | Exchange-specific pairs |

### Example Output File Format

`sorted_usdt_swap.txt`:
```
BINANCE:BTCUSDT - Market Cap: $1,000,000,000,000, Volume: $10,000,000,000
BINANCE:ETHUSDT - Market Cap: $200,000,000,000, Volume: $5,000,000,000
BINANCE:BNBUSDT - Market Cap: $50,000,000,000, Volume: $2,000,000,000
```

### Console Output

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

## Performance Tips

### Reduce API Calls

```bash
# Use cached market data when possible
uv run sandwich --base usdtperp --get-pairs

# Fetch market data only once per day
uv run sandwich --fetch
uv run sandwich --base usdtperp --get-pairs
uv run sandwich --base usdc --get-pairs
```

### Parallel Processing (Advanced)

```bash
# Process multiple exchanges in parallel
uv run sandwich --base usdtperp --fetch --get-pairs --exchange binance &
uv run sandwich --base usdtperp --get-pairs --exchange hyperliquid &
uv run sandwich --base usdtperp --get-pairs --exchange bybit &
wait
```

## Integration with TradingView

### Importing Pairs into TradingView

1. Open TradingView
2. Click on "Watchlist" (top-left corner)
3. Click on the gear icon (⚙️) to edit watchlist
4. Click "Import" and select your `sorted_<currency>_<type>.txt` file
5. Click "Apply"

### Watchlist Management

```bash
# Create a comprehensive watchlist
uv run sandwich --base usdtperp --fetch --get-pairs
uv run sandwich --base usdc --fetch --get-pairs
uv run sandwich --base fdusdperp --fetch --get-pairs

# Combine into single file
cat sorted_usdt_swap.txt sorted_usdc_spot.txt sorted_fdusd_swap.txt > comprehensive_watchlist.txt
```

## Common Use Cases

### Day Trading Setup

```bash
# Morning routine: Fetch fresh data and pairs
uv run sandwich --base usdtperp --fetch --get-pairs
uv run sandwich --base usdc --fetch --get-pairs

# Import both watchlists into TradingView
```

### Arbitrage Opportunities

```bash
# Fetch pairs from multiple exchanges
uv run sandwich --base usdtperp --get-pairs --exchange binance
uv run sandwich --base usdtperp --get-pairs --exchange bybit
uv run sandwich --base usdtperp --get-pairs --exchange okx

# Find overlapping pairs
comm -12 binance_usdt_swap_pairs.txt bybit_usdt_swap_pairs.txt > overlapping_pairs.txt
```

### Market Analysis

```bash
# Fetch and analyze market data
uv run sandwich --fetch
python -c "
import json
with open('coingecko_data.json') as f:
    data = json.load(f)
top_10 = sorted(data.items(), key=lambda x: x[1]['market_cap'], reverse=True)[:10]
for symbol, metrics in top_10:
    print(f'{symbol}: ${metrics[\"market_cap\"]:,}')
"
```

## Troubleshooting Common Scenarios

### I'm getting rate limited by CoinGecko

**Solution:**
```bash
# Reduce frequency of fetch calls
uv run sandwich --fetch  # Once per day
uv run sandwich --base usdtperp --get-pairs  # Use cached data
```

### Pairs are not matching across exchanges

**Solution:**
```bash
# Check if exchanges use same pair format
uv run sandwich --base usdtperp --get-pairs --exchange binance
uv run sandwich --base usdtperp --get-pairs --exchange hyperliquid

# Compare the outputs
diff binance_usdt_swap_pairs.txt hyperliquid_usdt_swap_pairs.txt
```
