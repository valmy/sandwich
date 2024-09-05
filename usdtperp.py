import ccxt
import pprint

def get_usdt_perpetual_pairs():
    """
    Retrieves USDT perpetual pairs from Binance using the ccxt library.

    Returns:
        list: A list of USDT perpetual pairs.
    """
    # Initialize the Binance exchange
    exchange = ccxt.binance()

    # Fetch all markets
    markets = exchange.load_markets()

    # Filter for swap markets only
    # swap_markets = {symbol: market for symbol, market in markets.items() if market['base'] == 'WAVES' and market['quote'] == 'USDT' and market['swap']}
    
    # Uncomment the following lines if you want to print the filtered swap markets
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(swap_markets)

    # Filter for USDT perpetual pairs
    usdt_perp_pairs = [symbol for symbol, market in markets.items() if market['active'] and market['quote'] == 'USDT' and market['swap']]

    return usdt_perp_pairs

def save_usdt_perp_pairs_for_tradingview(usdt_perp_pairs, filename="usdt_perp_pairs.txt"):
    """
    Converts USDT perpetual pairs to a format importable in TradingView and saves them to a file.

    Args:
        usdt_perp_pairs (list): A list of USDT perpetual pairs.
        filename (str): The name of the file to save the pairs to. Defaults to "usdt_perp_pairs.txt".

    Returns:
        None
    """
    with open(filename, "w") as f:
        for pair in usdt_perp_pairs:
            # Convert pair format from 'BTC/USDT:USDT' to 'BINANCE:BTCUSDTPERP'
            symbol = pair.split(':')[0].replace("/", "")
            tradingview_format = f"BINANCE:{symbol}PERP\n"
            f.write(tradingview_format)
    
    print(f"USDT perpetual pairs saved to {filename} in TradingView format.")

# Example usage
if __name__ == "__main__":
    print("Getting USDT perpetual pairs...")
    usdt_perp_pairs = get_usdt_perpetual_pairs()
    print(f"USDT perpetual pairs: {usdt_perp_pairs}")
    save_usdt_perp_pairs_for_tradingview(usdt_perp_pairs)
