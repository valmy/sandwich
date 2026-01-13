def get_coingecko_market_data():
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "image": "https://example.com/btc.png",
            "current_price": 91802.0,
            "market_cap": 1833787747268,
            "market_cap_rank": 1,
            "fully_diluted_valuation": 1833787747268,
            "total_volume": 45339514765,
            "high_24h": 92190.0,
            "low_24h": 90129.0,
            "price_change_24h": 519.26,
            "price_change_percentage_24h": 0.56884,
            "market_cap_change_24h": 8806481769,
            "market_cap_change_percentage_24h": 0.48255,
            "circulating_supply": 19975187.0,
            "total_supply": 19975187.0,
            "max_supply": 21000000.0,
            "ath": 126080.0,
            "ath_change_percentage": -27.18724,
            "atl": 67.81,
            "atl_change_percentage": 135283.57255,
            "roi": None,
            "last_updated": "2026-01-13T07:52:20.863Z",
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "image": "https://example.com/eth.png",
            "current_price": 3119.41,
            "market_cap": 376498909677,
            "market_cap_rank": 2,
            "fully_diluted_valuation": 376498909677,
            "total_volume": 22122492707,
            "high_24h": 3141.18,
            "low_24h": 3071.03,
            "price_change_24h": -14.34,
            "price_change_percentage_24h": -0.45772,
            "market_cap_change_24h": -1772483515.9054565,
            "market_cap_change_percentage_24h": -0.46857,
            "circulating_supply": 120694705.6171877,
            "total_supply": 120694705.6171877,
            "max_supply": None,
            "ath": 4946.05,
            "ath_change_percentage": -36.93117,
            "ath_date": "2025-08-24T19:21:03.333Z",
            "atl": 0.432979,
            "atl_change_percentage": 720354.32836,
            "atl_date": "2015-10-20T00:00:00.000Z",
            "roi": {
                "times": 44.42543217719102,
                "currency": "btc",
                "percentage": 4442.543217719101,
            },
            "last_updated": "2026-01-13T07:52:20.585Z",
        },
    ]


def get_coingecko_page_data(page=1):
    if page == 1:
        return [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 91802.0,
                "market_cap": 1833787747268,
                "market_cap_rank": 1,
                "total_volume": 45339514765,
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 3119.41,
                "market_cap": 376498909677,
                "market_cap_rank": 2,
                "total_volume": 22122492707,
            },
            {
                "id": "tether",
                "symbol": "usdt",
                "name": "Tether",
                "current_price": 0.998822,
                "market_cap": 186713283278,
                "market_cap_rank": 3,
                "total_volume": 1234567890,
            },
        ]
    elif page == 2:
        return [
            {
                "id": "solana",
                "symbol": "sol",
                "name": "Solana",
                "current_price": 100.0,
                "market_cap": 45000000000,
                "market_cap_rank": 10,
                "total_volume": 2000000000,
            },
            {
                "id": "ripple",
                "symbol": "xrp",
                "name": "XRP",
                "current_price": 0.5,
                "market_cap": 27000000000,
                "market_cap_rank": 11,
                "total_volume": 1500000000,
            },
        ]
    return []


def get_coingecko_rate_limit_response():
    return {"status_code": 429, "json": [], "content": b""}


def get_coingecko_error_response():
    return {"status_code": 500, "json": [], "content": b"Internal Server Error"}


def get_coingecko_empty_response():
    return {"status_code": 200, "json": [], "content": b"[]"}
