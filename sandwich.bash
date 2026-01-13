#!/bin/bash

# Sandwich script to generate filtered pairs lists
# This script performs the following steps:
# 1. Fetch market data (500 coins from CoinGecko) and get USDT spot pairs (with sorting)
# 2. Get USDT perp pairs from Binance
# 3. Filter USDT perp pairs against Hyperliquid availability

set -e  # Exit on any error

echo "=== Starting Sandwich Pair Generation ==="
echo

echo "Step 1: Fetching market data and generating USDT spot pairs..."
uv run sandwich --fetch --base usdt --get-pairs
echo "✓ USDT spot pairs generated (sorted_usdt_spot.txt)"
echo

echo "Step 2: Generating USDT perp pairs from Binance..."
uv run sandwich --base usdtperp --get-pairs
echo "✓ USDT perp pairs generated (usdt_swap_pairs.txt)"
echo

echo "Step 3: Filtering USDT perp pairs against Hyperliquid availability..."
uv run sandwich --base usdtperp --hyperliquid
echo "✓ Filtered pairs generated (usdt_swap_hype_pairs.txt)"
echo

echo "=== All steps completed successfully! ==="
echo
echo "Generated files:"
echo "  - sorted_usdt_spot.txt    (USDT spot pairs, volume-sorted)"
echo "  - usdt_swap_pairs.txt     (All USDT perp pairs from Binance)"
echo "  - usdt_swap_hype_pairs.txt (USDT perp pairs available on Hyperliquid)"
echo "  - sorted_usdt_swap_hype.txt (Filtered pairs, volume-sorted)"
echo
echo "The usdt_swap_hype_pairs.txt file contains only Binance futures pairs"
echo "that are available on Hyperliquid exchange, ready for TradingView import."