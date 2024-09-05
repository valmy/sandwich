import ccxt

def get_fdusd_spot_pairs():
    """
    Retrieves FDUSD spot pairs from Binance using the ccxt library.

    Returns:
        list: A list of FDUSD spot pairs.
    """
    # Initialize the Binance exchange
    exchange = ccxt.binance()

    # Fetch all markets
    markets = exchange.load_markets()

    # Filter for FDUSD spot pairs
    fdusd_pairs = [symbol for symbol, market in markets.items() if market['active'] and market['quote'] == 'FDUSD' and market['spot']]

    return fdusd_pairs

def save_fdusd_pairs_for_tradingview(fdusd_pairs, filename="fdusd_pairs.txt"):
    """
    Converts FDUSD spot pairs to a format importable in TradingView and saves them to a file.

    Args:
        fdusd_pairs (list): A list of FDUSD spot pairs.
        filename (str): The name of the file to save the pairs to. Defaults to "fdusd_pairs.txt".

    Returns:
        None
    """
    with open(filename, "w") as f:
        for pair in fdusd_pairs:
            # Convert pair format from 'BTC/FDUSD' to 'BINANCE:BTCFDUSD'
            symbol = pair.replace("/", "")
            tradingview_format = f"BINANCE:{symbol}\n"
            f.write(tradingview_format)
    
    print(f"FDUSD pairs saved to {filename} in TradingView format.")

# Example usage
if __name__ == "__main__":
    print("Getting FDUSD spot pairs...")
    fdusd_pairs = get_fdusd_spot_pairs()
    print(f"FDUSD spot pairs: {fdusd_pairs}")
    save_fdusd_pairs_for_tradingview(fdusd_pairs)


