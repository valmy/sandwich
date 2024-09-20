Python Scripts to maintain TradingView lists from Binance Exchange.
It also fetches volume data from coingecko and then sorted the lists

## Usage

 Usage: rye run sandwich [OPTIONS]

 Options:
  --base  TEXT  [default usdtperp]                 Base currency (usdtperp|usdc|fdusd)
  --fetch  or  --no-fetch [default: no-fetch]      Get volume data from coingecko
  --get-pairs or --no-get-pairs  [default: no-get-pairs]  Get pair data from Binance

Example:
```
rye run sandwich --base usdc --fetch --get-pairs
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
