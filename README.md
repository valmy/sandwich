Python Scripts to maintain TradingView lists from Binance Exchange.
It also fetches volume data from coingecko and then sorted the lists

## Usage

Usage: rye run sandwich [OPTIONS]

Options:
  --base TEXT          Base currency/type [default: usdtperp]
                       Options include: usdtperp, usdc, fdusd
                       Note: Adding 'perp' suffix will use 'swap' market type

  --fetch/--no-fetch   [default: no-fetch]
                       Get volume data from CoinGecko

  --get-pairs/--no-get-pairs  [default: no-get-pairs]
                       Get pair data from Binance

  --hyperliquid/--no-hyperliquid  [default: no-hyperliquid]
                       Use Hyperliquid exchange data instead of Binance

### Examples:

```bash
# Fetch USDC pairs from Binance and sort with CoinGecko volume data
rye run sandwich --base usdc --fetch --get-pairs

# Work with USDT perpetual pairs
rye run sandwich --base usdtperp --get-pairs

# Fetch and process Hyperliquid exchange data
rye run sandwich --hyperliquid --fetch

# Only sort existing pair data (no fetching)
rye run sandwich --base fdusd
```

## Installation

To install rye, follow these steps:

1. Install rye using the official installation script:

curl -sSf https://rye-up.com/get | bash

2. Restart your terminal or run `source ~/.bashrc` (or the appropriate config file) to apply the changes.

3. Verify the installation by running:

rye --version

Now you're ready to use rye with this project.

## Contributing
As experiment using AI to write code:
 * [Github Copilot](https://github.com/features/copilot)
 * [Cursor AI](https://www.cursor.com/)
 * [Sourcegraph Cody](https://sourcegraph.com/cody)
