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
        json.dump(all_data, f)

    print(f"Market data saved successfully to {file_name}")
