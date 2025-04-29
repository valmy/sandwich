import json

def remove_prefix_suffix(s):
    """
    Removes the prefix 'BINANCE:' and the suffix 'PERP' from the given string.

    Args:
        s (str): The input string.

    Returns:
        str: The modified string with the prefix and suffix removed.
    """
    if s.startswith('BINANCE:'):
        s = s.replace('BINANCE:', '', 1)
    if s.endswith('PERP'):
        s = s[:-4]
    return s

def find_symbol_in_lines(item, lines, base_currency='USDT'):
    """
    Finds the symbol in the list of lines.

    Args:
        item (str): The symbol data to find.
        lines (list): A list of strings.
        base_currency (str): The base currency to use (default is 'USDT').

    Returns:
        str: The line containing the symbol, or an empty string if the symbol is not found.
    """
    excluded_currencies = ['USDC', 'FDUSD', 'EUR']
    for line in lines:
        symbol = item["symbol"].upper() + base_currency
        symbol_in_line = remove_prefix_suffix(line)
        if not any(symbol == f'{curr}{base_currency}' for curr in excluded_currencies) and (symbol == symbol_in_line or ('1000' + symbol) == symbol_in_line):
            return line
    return ''

def sort_market_data(base_currency, market_type, is_hyperliquid=False):
    """
    Sorts market data based on symbol and market cap rank.

    Args:
        base_currency (str): The base currency to use (e.g., 'USDT', 'USDC').
        market_type (str): The type of market ('swap' or 'spot').
        is_hyperliquid (bool): Whether to sort Hyperliquid pairs data.

    Returns:
        None
    """
    # open json file
    json_file = 'marketcap.json'

    # Determine file names based on whether we're sorting Hyperliquid pairs
    if is_hyperliquid:
        txt_file = f'{base_currency.lower()}_{market_type}_hype_pairs.txt'
        sorted_file = f'sorted_{base_currency.lower()}_{market_type}_hype.txt'
    else:
        txt_file = f'{base_currency.lower()}_{market_type}_pairs.txt'
        sorted_file = f'sorted_{base_currency.lower()}_{market_type}.txt'

    with open(json_file, 'r') as f:
        # read file
        data = f.read()
        # parse file
        mcap = json.loads(data)[0:500]

        # open txt file
        with open(txt_file, 'r') as g:
            data = g.read()
            # split the data into a list of lines
            lines = data.splitlines()

            sorted_data = ''
            # Sort market data by total_volume descending
            mcap_sorted = sorted(mcap, key=lambda x: x["total_volume"], reverse=True)

            sorted_symbols = set()
            for i in mcap_sorted:
                # total_volume = int(i["total_volume"]) if isinstance(i["total_volume"], (float, str)) else i["total_volume"]
                # print(f'{i["symbol"]} - {i["market_cap_rank"]} - {total_volume}')

                # find the symbol in the list of lines
                line = find_symbol_in_lines(i, lines, base_currency)
                if line:
                    sorted_data += line + '\n'
                    sorted_symbols.add(line)

            # print the number of lines
            print(f'{len(sorted_data.splitlines())} lines')

            # Append unsorted pairs
            unsorted_count = 0
            for line in lines:
                if line not in sorted_symbols:
                    sorted_data += line + '\n'
                    unsorted_count += 1
            print(f'Number of unsorted symbols: {unsorted_count}')

            # write the sorted data back to a new file
            with open(sorted_file, 'w') as h:
                h.write(sorted_data)

# download_file(url, file_path)

# save_market_data()

# sort_market_data()
