import ccxt
import os
import re

def get_pairs(base_currency='USDC', type='swap'):
    """
    Retrieves pairs from Hyperliquid exchange using ccxt.

    Args:
        base_currency (str): The base currency to filter pairs (e.g., 'USDC').
                            Note: Hyperliquid uses USDC as the base currency.
        type (str): The type of pairs to retrieve ('swap' for perpetual pairs or 'spot' for spot pairs).

    Returns:
        list: A list of trading pairs from Hyperliquid.
    """
    try:
        # Use hyperliquid directly through ccxt
        exchange = ccxt.hyperliquid()
        markets = exchange.load_markets()

        # Extract pairs with USDC as quote currency (Hyperliquid uses USDC)
        pairs = [symbol for symbol, market in markets.items()
                if market['active'] and market['quote'] == base_currency and market.get(type, False)]

        return pairs
    except Exception as e:
        print(f"Error fetching Hyperliquid data via ccxt: {e}")
        return []

def normalize_coin_name(coin):
    """
    Normalize coin names by handling special prefixes.

    Args:
        coin (str): The coin name to normalize.

    Returns:
        str: Normalized coin name.
    """
    # Handle case where Hyperliquid uses 'k' prefix and Binance uses '1000' prefix
    if coin.startswith('k') and len(coin) > 1 and coin[1].isupper():
        return coin[1:]  # Remove the 'k' prefix

    # Handle case where Binance uses '1000' prefix
    if coin.startswith('1000'):
        return coin[4:]  # Remove the '1000' prefix

    return coin

def load_pairs_from_file(base_currency='USDT', type='swap'):
    """
    Loads pairs from an existing file in TradingView format.

    Args:
        base_currency (str): The base currency of the pairs file (e.g., 'USDT').
        type (str): The type of pairs ('swap' or 'spot').

    Returns:
        list: A list of trading pairs in CCXT format.
    """
    filename = f"{base_currency.lower()}_{type}_pairs.txt"
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. No pairs will be loaded.")
        return []

    pairs = []
    with open(filename, "r") as f:
        for line in f:
            # Extract the symbol from TradingView format (e.g., BINANCE:BTCUSDTPERP -> BTC/USDT)
            line = line.strip()
            if line.startswith("BINANCE:"):
                symbol = line.split(':', 1)[1]
                # Remove PERP suffix if present
                if type == 'swap' and symbol.endswith("PERP"):
                    symbol = symbol[:-4]

                # Convert to CCXT format (e.g., BTCUSDT -> BTC/USDT)
                if base_currency in symbol:
                    base_index = symbol.find(base_currency)
                    coin = symbol[:base_index]
                    ccxt_symbol = f"{coin}/{base_currency}"
                    pairs.append(ccxt_symbol)

    print(f"Loaded {len(pairs)} pairs from {filename}")
    return pairs

def get_ccxt_pairs(exchange_id='binance', base_currency='USDT', type='swap'):
    """
    Retrieves pairs from any exchange supported by ccxt.

    Args:
        exchange_id (str): The ccxt exchange ID (e.g., 'binance', 'bybit', 'okx').
        base_currency (str): The base currency to filter pairs (e.g., 'USDT').
        type (str): The type of pairs to retrieve ('swap' for perpetual pairs or 'spot' for spot pairs).

    Returns:
        list: A list of trading pairs for the specified exchange and base currency.
    """
    try:
        # Dynamically create exchange instance based on exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        markets = exchange.load_markets()

        pairs = [symbol for symbol, market in markets.items()
                      if market['active'] and market['quote'] == base_currency and market.get(type, False)]

        return pairs
    except Exception as e:
        print(f"Error fetching pairs from {exchange_id}: {e}")
        return []

def match_with_binance_pairs(hyperliquid_pairs, binance_base_currency='USDT', type='swap'):
    """
    Matches Hyperliquid pairs (USDC) with equivalent Binance pairs (USDT) for TradingView compatibility.
    Handles special cases like 'k' prefix in Hyperliquid and '1000' prefix in Binance.

    Args:
        hyperliquid_pairs (list): List of Hyperliquid pairs with USDC as the base currency.
        binance_base_currency (str): The base currency for Binance pairs (typically 'USDT').
        type (str): The type of Binance pairs ('swap' for perpetual or 'spot').

    Returns:
        list: List of matched Binance pairs that exist on both exchanges.
    """
    # Always load Binance pairs with USDT base currency
    binance_pairs = load_pairs_from_file(binance_base_currency, type)
    if not binance_pairs:
        print(f"No pairs found in file, fetching from Binance API instead...")
        binance_pairs = get_ccxt_pairs('binance', binance_base_currency, type)

    # Match Hyperliquid pairs with Binance pairs (ignoring the base currency difference)
    matched_pairs = []
    missing_pairs = []

    # Create a dictionary of normalized coin names to Binance pairs for faster lookups
    binance_normalized = {}
    for binance_pair in binance_pairs:
        coin = binance_pair.split('/')[0]
        normalized_coin = normalize_coin_name(coin)
        binance_normalized[normalized_coin] = binance_pair

    special_matches = 0
    normal_matches = 0

    for hl_pair in hyperliquid_pairs:
        # Extract the coin part (e.g., BTC/USDC -> BTC)
        coin = hl_pair.split('/')[0]
        normalized_coin = normalize_coin_name(coin)

        # Look for match in the normalized dictionary
        if normalized_coin in binance_normalized:
            matched_pairs.append(binance_normalized[normalized_coin])
            if coin != normalized_coin or binance_normalized[normalized_coin].split('/')[0] != normalized_coin:
                special_matches += 1
                print(f"Special match: {coin} (Hyperliquid) -> {binance_normalized[normalized_coin].split('/')[0]} (Binance)")
            else:
                normal_matches += 1
        else:
            missing_pairs.append(hl_pair)

    # Print missing pairs
    if missing_pairs:
        print(f"\nPairs not found in Binance {type} {binance_base_currency}:")
        for pair in missing_pairs:
            print(f"  {pair}")

    print(f"Found {len(matched_pairs)} matching pairs between Hyperliquid (USDC) and Binance (USDT)")
    print(f"  - Normal matches: {normal_matches}")
    print(f"  - Special prefix matches (k -> 1000): {special_matches}")
    print(f"Found {len(missing_pairs)} pairs that exist on Hyperliquid but not on Binance")

    return matched_pairs

def match_pairs_between_exchanges(source_pairs, target_exchange_id='binance', base_currency='USDT', type='swap'):
    """
    Matches pairs from one source with pairs from a target exchange.
    Handles special cases like 'k' prefix and '1000' prefix.

    Args:
        source_pairs (list): List of source exchange pairs.
        target_exchange_id (str): The ccxt exchange ID to match with.
        base_currency (str): The base currency for target exchange pairs.
        type (str): The type of target exchange pairs ('swap' for perpetual or 'spot').

    Returns:
        list: List of matched target exchange pairs that exist on both exchanges.
    """
    # Get target pairs from saved file first if target is Binance, fall back to API
    if target_exchange_id.lower() == 'binance':
        target_pairs = load_pairs_from_file(base_currency, type)
        if not target_pairs:
            print(f"No pairs found in file, fetching from {target_exchange_id} API instead...")
            target_pairs = get_ccxt_pairs(target_exchange_id, base_currency, type)
    else:
        target_pairs = get_ccxt_pairs(target_exchange_id, base_currency, type)

    # Create a dictionary of normalized coin names to target pairs for faster lookups
    target_normalized = {}
    for target_pair in target_pairs:
        coin = target_pair.split('/')[0]
        normalized_coin = normalize_coin_name(coin)
        target_normalized[normalized_coin] = target_pair

    matched_pairs = []
    missing_pairs = []
    special_matches = 0
    normal_matches = 0

    for source_pair in source_pairs:
        coin = source_pair.split('/')[0]
        normalized_coin = normalize_coin_name(coin)

        # Look for match in the normalized dictionary
        if normalized_coin in target_normalized:
            matched_pairs.append(target_normalized[normalized_coin])
            if coin != normalized_coin or target_normalized[normalized_coin].split('/')[0] != normalized_coin:
                special_matches += 1
                print(f"Special match: {coin} -> {target_normalized[normalized_coin].split('/')[0]}")
            else:
                normal_matches += 1
        else:
            missing_pairs.append(source_pair)

    # Print missing pairs
    if missing_pairs:
        print(f"\nPairs not found in {target_exchange_id} {type} {base_currency}:")
        for pair in missing_pairs:
            print(f"  {pair}")

    print(f"Found {len(matched_pairs)} matching pairs in {target_exchange_id}")
    print(f"  - Normal matches: {normal_matches}")
    print(f"  - Special prefix matches: {special_matches}")
    print(f"Found {len(missing_pairs)} pairs that don't exist in {target_exchange_id}")

    return matched_pairs

def save_hyperliquid_pairs_for_tradingview(matched_pairs, base_currency, type='swap'):
    """
    Saves Hyperliquid-matched Binance pairs to a file in TradingView format.

    Args:
        matched_pairs (list): List of matched pairs.
        base_currency (str): The base currency (e.g., 'USDT').
        type (str): The type of pairs ('swap' or 'spot').

    Returns:
        None
    """
    filename = f"{base_currency.lower()}_{type}_hype_pairs.txt"
    type_str = 'PERP' if type == 'swap' else ''

    with open(filename, "w") as f:
        for pair in matched_pairs:
            symbol = pair.split(':')[0].replace("/", "")
            tradingview_format = f"BINANCE:{symbol}{type_str}\n"
            f.write(tradingview_format)

    print(f"Hyperliquid-matched {base_currency} {type} pairs saved to {filename} in TradingView format.")

def save_pairs_for_tradingview(pairs, exchange_id='binance', base_currency='USDT', type='swap', filename=None):
    """
    Converts pairs to a format importable in TradingView and saves them to a file.

    Args:
        pairs (list): A list of trading pairs.
        exchange_id (str): The exchange ID for TradingView (e.g., 'BINANCE', 'BYBIT').
        base_currency (str): The base currency of the pairs.
        type (str): The type of pairs ('swap' or 'spot').
        filename (str, optional): The name of the file to save the pairs to.
                                  If not provided, it defaults to "{exchange_id}_{base_currency.lower()}_{type}_pairs.txt".

    Returns:
        None
    """
    if filename is None:
        filename = f"{exchange_id.lower()}_{base_currency.lower()}_{type}_pairs.txt"

    type_str = 'PERP' if type == 'swap' else ''
    exchange_id_upper = exchange_id.upper()

    with open(filename, "w") as f:
        for pair in pairs:
            symbol = pair.split(':')[0].replace("/", "")
            tradingview_format = f"{exchange_id_upper}:{symbol}{type_str}\n"
            f.write(tradingview_format)

    print(f"{exchange_id} {base_currency} {type} pairs saved to {filename} in TradingView format.")

def get_and_save_hyperliquid_pairs(hyperliquid_base_currency='USDC', binance_base_currency='USDT', type='swap'):
    """
    Retrieves pairs from Hyperliquid (USDC), matches them with Binance (USDT), and saves them.

    Args:
        hyperliquid_base_currency (str): The base currency for Hyperliquid (typically 'USDC').
        binance_base_currency (str): The base currency for Binance matching (typically 'USDT').
        type (str): The type of pairs ('swap' for perpetual or 'spot').

    Returns:
        None
    """
    print(f"Getting Hyperliquid pairs using ccxt and matching with Binance {binance_base_currency} {type} pairs...")
    hyperliquid_pairs = get_pairs(hyperliquid_base_currency, type)
    print(f"Hyperliquid pairs: {len(hyperliquid_pairs)} found")

    matched_pairs = match_with_binance_pairs(hyperliquid_pairs, binance_base_currency, type)
    print(f"Matched pairs: {len(matched_pairs)} found")

    save_hyperliquid_pairs_for_tradingview(matched_pairs, binance_base_currency, type)

def get_and_save_ccxt_pairs(exchange_id='binance', base_currency='USDT', type='swap', use_existing_binance=True):
    """
    Retrieves and saves pairs for a specific exchange using ccxt.
    If use_existing_binance is True and exchange is not Binance, it will filter pairs against existing Binance pairs.

    Args:
        exchange_id (str): The ccxt exchange ID (e.g., 'binance', 'bybit', 'okx').
        base_currency (str): The base currency to process (e.g., 'USDT', 'USDC', 'FDUSD').
        type (str): The type of pairs ('swap' for perpetual or 'spot' for spot).
        use_existing_binance (bool): Whether to filter pairs against existing Binance pairs.

    Returns:
        list: A list of pairs retrieved from the exchange.
    """
    print(f"Getting {exchange_id} {base_currency} {type} pairs...")
    pairs = get_ccxt_pairs(exchange_id, base_currency, type)
    print(f"{exchange_id} {base_currency} {type} pairs: {len(pairs)} found")

    if use_existing_binance and exchange_id.lower() != 'binance':
        # Filter against Binance pairs
        binance_pairs = load_pairs_from_file(base_currency, type)
        if binance_pairs:
            print(f"Filtering {exchange_id} pairs against Binance pairs...")
            filtered_pairs = []
            missing_pairs = []

            for pair in pairs:
                coin = pair.split('/')[0]
                found = False
                for binance_pair in binance_pairs:
                    if binance_pair.split('/')[0] == coin:
                        filtered_pairs.append(pair)
                        found = True
                        break

                if not found:
                    missing_pairs.append(pair)

            # Print missing pairs
            if missing_pairs:
                print(f"\nPairs in {exchange_id} but not in Binance {type} {base_currency}:")
                for pair in missing_pairs:
                    print(f"  {pair}")

            print(f"Found {len(filtered_pairs)} pairs that exist in both {exchange_id} and Binance")
            print(f"Found {len(missing_pairs)} pairs that exist only in {exchange_id}")

            pairs = filtered_pairs

    if pairs:
        save_pairs_for_tradingview(pairs, exchange_id, base_currency, type)

    return pairs

# Example usage
if __name__ == "__main__":
    # Get pairs from Hyperliquid (USDC) and match with Binance (USDT)
    get_and_save_hyperliquid_pairs('USDC', 'USDT', 'swap')

    # Also works for spot markets
    # get_and_save_hyperliquid_pairs('USDC', 'USDT', 'spot')

    # Get pairs from specific exchanges using ccxt
    # get_and_save_ccxt_pairs('binance', 'USDT', 'swap')
    # get_and_save_ccxt_pairs('bybit', 'USDT', 'swap', use_existing_binance=True)
    # get_and_save_ccxt_pairs('okx', 'USDT', 'swap', use_existing_binance=True)
