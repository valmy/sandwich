import ccxt

def get_pairs(base_currency: str = 'USDT', type='swap'):
    """
    Retrieves perpetual pairs for a specific base currency from Binance using the ccxt library.

    Args:
        base_currency (str): The base currency to filter pairs (e.g., 'USDT', 'USDC', 'FDUSD').
        type (str): The type of pairs to retrieve ('swap' for perpetual pairs or 'spot' for spot pairs).

    Returns:
        list: A list of perpetual pairs for the specified base currency.
    """
    exchange = ccxt.binance()
    markets = exchange.load_markets()

    pairs = [symbol for symbol, market in markets.items()
                  if market['active'] and market['quote'] == base_currency and market[type]]

    return pairs

def save_pairs_for_tradingview(pairs, base_currency, type = 'swap', filename=None):
    """
    Converts pairs to a format importable in TradingView and saves them to a file.

    Args:
        pairs (list): A list of trading pairs.
        base_currency (str): The base currency of the pairs.
        filename (str, optional): The name of the file to save the pairs to.
                                  If not provided, it defaults to "{base_currency.lower()}_perp_pairs.txt".

    Returns:
        None
    """
    if filename is None:
        filename = f"{base_currency.lower()}_{type}_pairs.txt"

    type_str = 'PERP' if type == 'swap' else ''

    with open(filename, "w") as f:
        for pair in pairs:
            symbol = pair.split(':')[0].replace("/", "")
            tradingview_format = f"BINANCE:{symbol}{type_str}\n"
            f.write(tradingview_format)

    print(f"{base_currency} {type} pairs saved to {filename} in TradingView format.")

def get_and_save_pairs(base_currency = 'USDT', type = 'swap'):
    """
    Retrieves and saves perpetual pairs for a specific base currency.

    Args:
        base_currency (str): The base currency to process (e.g., 'USDT', 'USDC', 'FDUSD').
        type (str): The type of pairs to retrieve ('swap' for perpetual pairs or 'spot' for spot pairs).

    Returns:
        None
    """
    print(f"Getting {base_currency} {type} pairs...")
    pairs = get_pairs(base_currency, type)
    print(f"{base_currency} {type} pairs: {len(pairs)} found")
    save_pairs_for_tradingview(pairs, base_currency, type)

# Example usage
if __name__ == "__main__":
    # Get and save USDT perpetual pairs
    get_and_save_pairs('USDT', 'swap')

    # Get and save USDC spot pairs
    # get_and_save_pairs('USDC', 'spot')

    # Get and save FDUSD perpetual pairs
    # get_and_save_pairs('FDUSD', 'swap')
