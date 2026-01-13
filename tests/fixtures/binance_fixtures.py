def get_binance_markets_swap():
    return {
        "BTC/USDT:USDT": {
            "id": "BTCUSDT",
            "symbol": "BTC/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "ETH/USDT:USDT": {
            "id": "ETHUSDT",
            "symbol": "ETH/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "SOL/USDT:USDT": {
            "id": "SOLUSDT",
            "symbol": "SOL/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "1000PEPE/USDT:USDT": {
            "id": "PEPEUSDT",
            "symbol": "1000PEPE/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "XRP/USDT:USDT": {
            "id": "XRPUSDT",
            "symbol": "XRP/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "BNB/USDT:USDT": {
            "id": "BNBUSDT",
            "symbol": "BNB/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "USDC/USDT:USDT": {
            "id": "USDCUSDT",
            "symbol": "USDC/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
        "FDUSD/USDT:USDT": {
            "id": "FDUSDUSDT",
            "symbol": "FDUSD/USDT:USDT",
            "active": True,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
    }


def get_binance_markets_spot():
    return {
        "BTC/USDT": {
            "id": "BTCUSDT",
            "symbol": "BTC/USDT",
            "active": True,
            "quote": "USDT",
            "swap": False,
            "spot": True,
        },
        "ETH/USDT": {
            "id": "ETHUSDT",
            "symbol": "ETH/USDT",
            "active": True,
            "quote": "USDT",
            "swap": False,
            "spot": True,
        },
        "USDC/USDT": {
            "id": "USDCUSDT",
            "symbol": "USDC/USDT",
            "active": True,
            "quote": "USDT",
            "swap": False,
            "spot": True,
        },
    }


def get_binance_empty_markets():
    return {}


def get_binance_inactive_markets():
    return {
        "BTC/USDT:USDT": {
            "id": "BTCUSDT",
            "symbol": "BTC/USDT:USDT",
            "active": False,
            "quote": "USDT",
            "swap": True,
            "spot": False,
        },
    }


def get_binance_usdc_swap_markets():
    return {
        "BTC/USDC:USDC": {
            "id": "BTCUSDC",
            "symbol": "BTC/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "ETH/USDC:USDC": {
            "id": "ETHUSDC",
            "symbol": "ETH/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
    }


def get_binance_fdusd_swap_markets():
    return {
        "BTC/FDUSD:FDUSD": {
            "id": "BTCFDUSD",
            "symbol": "BTC/FDUSD:FDUSD",
            "active": True,
            "quote": "FDUSD",
            "swap": True,
            "spot": False,
        },
    }


def get_tradingview_format_pairs_swap():
    return [
        "BINANCE:BTCUSDTPERP",
        "BINANCE:ETHUSDTPERP",
        "BINANCE:SOLUSDTPERP",
        "BINANCE:1000PEPEUSDTPERP",
        "BINANCE:XRPUSDTPERP",
        "BINANCE:BNBUSDTPERP",
    ]


def get_tradingview_format_pairs_spot():
    return [
        "BINANCE:BTCUSDT",
        "BINANCE:ETHUSDT",
        "BINANCE:USDCUSDT",
    ]
