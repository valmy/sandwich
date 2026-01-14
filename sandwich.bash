#!/bin/bash

# Sandwich script to generate filtered pairs lists
# This script performs the following steps:
# 1. Fetch market data (500 coins from CoinGecko) and get USDT spot pairs (with sorting)
# 2. Get USDT perp pairs from Binance
# 3. Filter USDT perp pairs against Hyperliquid availability

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures

# Validate that required commands exist
command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed or not in PATH" >&2; exit 1; }

echo "=== Starting Sandwich Pair Generation ==="
echo

echo "Step 1: Fetching market data and generating USDC spot pairs..."
if ! uv run sandwich --fetch --base usdc --get-pairs; then
    echo "Error: Failed to fetch market data or generate USDC spot pairs" >&2
    exit 1
fi
echo "✓ USDC spot pairs generated (sorted_usdc_spot.txt)"
echo

echo "Step 2: Generating USDT perp pairs from Binance..."
if ! uv run sandwich --base usdtperp --get-pairs; then
    echo "Error: Failed to generate USDT perp pairs" >&2
    exit 1
fi
echo "✓ USDT perp pairs generated (usdt_swap_pairs.txt)"
echo

echo "Step 3: Filtering USDT perp pairs against Hyperliquid availability..."
if ! uv run sandwich --base usdtperp --hyperliquid; then
    echo "Error: Failed to filter pairs against Hyperliquid" >&2
    exit 1
fi
echo "✓ Filtered pairs generated (usdt_swap_hype_pairs.txt)"
echo

echo "=== All steps completed successfully! ==="
echo
echo "Generated files:"
echo "  - sorted_usdc_spot.txt    (USDC spot pairs, volume-sorted)"
echo "  - usdt_swap_pairs.txt     (All USDT perp pairs from Binance)"
echo "  - usdt_swap_hype_pairs.txt (USDT perp pairs available on Hyperliquid)"
echo "  - sorted_usdt_swap_hype.txt (Filtered pairs, volume-sorted)"
echo
echo "The usdt_swap_hype_pairs.txt file contains only Binance futures pairs"
echo "that are available on Hyperliquid exchange, ready for TradingView import."