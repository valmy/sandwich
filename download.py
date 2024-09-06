import requests
import json
import time

def make_request(url, max_retries=5):
    for i in range(max_retries):
        response = requests.get(url)
        if response.status_code != 429:
            return response
        time.sleep(2 ** i)
    return None  # or raise an exception

def download_file(url, file_path):
    """
    Downloads a file from the specified URL and saves it to the given file path.

    Args:
        url (str): The URL of the file to download.
        file_path (str): The path where the downloaded file will be saved.

    Returns:
        None

    Raises:
        None
    """
    # Make a request to the URL
    response = make_request(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the response body to a file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully at {file_path}")
    else:
        print("Request failed with status code:", response.status_code)


def save_market_data(file_name='marketcap.json'):
    """
    Save market data from the Coingecko public API to a file.

    Args:
        file_name (str): The name of the file to save the market data to. Default is 'marketcap.json'.

    Returns:
        None
    """
    # coingecko public api coins/markets
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250'

    # Save the response body to a file
    with open(file_name, 'w') as f:
        all_data = []
        for page in range(1, 3):  # Get 2 pages
            # Page url:
            page_url = f'{url}&page={page}'
            print(page_url)
            # Make a request to the URL
            response = make_request(page_url)

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                all_data.extend(data)
            else:
                print(f"Request failed for page {page} with status code:", response.status_code)
                return

        # count and print the number of items in the list
        print(f"Number of items in the list: {len(all_data)}")
        # json.dump(all_data, f)
    print(f"Market data saved successfully to {file_name}")

def remove_prefix_suffix(s):
    """
    Removes the prefix 'BINANCE:' and the suffix 'PERP' from the given string.

    Args:
        s (str): The input string.

    Returns:
        str: The modified string with the prefix and suffix removed.
    """
    if s.startswith('BINANCE:') and s.endswith('PERP'):
        s = s.replace('BINANCE:', '', 1)
        s = s[:-4]
    return s

def find_symbol_in_lines(item, lines):
    """
    Finds the symbol in the list of lines.

    Args:
        item (str): The symbol data to find.
        lines (list): A list of strings.

    Returns:
        str: The line containing the symbol, or an empty string if the symbol is not found.
    """
    for line in lines:
        symbol = item["symbol"].upper() + 'USDT'
        symbol_in_line = remove_prefix_suffix(line)
        if symbol != 'USDCUSDT' and (symbol == symbol_in_line or ('1000' + symbol) == symbol_in_line):
            return line
    return ''

def sort_market_data(json_file='marketcap.json', txt_file='usdt_perp_futures.txt', sorted_file='sorted_usdt_perp.txt'):
    """
    Sorts market data based on symbol and market cap rank.

    Args:
        json_file (str): Path to the JSON file containing market data. Default is 'marketcap.json'.
        txt_file (str): Path to the TXT file containing additional data. Default is 'usdt_perp_futures.txt'.
        sorted_file (str): Path to the file where the sorted data will be written. Default is 'sorted_usdt_perp.txt'.

    Returns:
        None
    """
    # Rest of the code...
    # open json file
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

            for i in mcap_sorted:
                total_volume = int(i["total_volume"]) if isinstance(i["total_volume"], (float, str)) else i["total_volume"]
                print(f'{i["symbol"]} - {i["market_cap_rank"]} - {total_volume}')

                # find the symbol in the list of lines
                line = find_symbol_in_lines(i, lines)
                if line:
                    sorted_data += line + '\n'

            # write the sorted data back to a new file
            with open(sorted_file, 'w') as h:
                h.write(sorted_data)

url = 'https://sandwichfinance.blob.core.windows.net/files/binancefuturesf_usdt_perpetual_futures.txt'
file_path = 'usdt_perp_pairs.txt'

# download_file(url, file_path)

save_market_data()

sort_market_data()
