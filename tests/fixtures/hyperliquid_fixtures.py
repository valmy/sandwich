def get_hyperliquid_markets():
    return {
        "BTC/USDC:USDC": {
            "id": "BTC",
            "symbol": "BTC/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "ETH/USDC:USDC": {
            "id": "ETH",
            "symbol": "ETH/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "SOL/USDC:USDC": {
            "id": "SOL",
            "symbol": "SOL/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "KPEPE/USDC:USDC": {
            "id": "PEPE",
            "symbol": "KPEPE/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "KSHIB/USDC:USDC": {
            "id": "SHIB",
            "symbol": "KSHIB/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "KNEIRO/USDC:USDC": {
            "id": "NEIRO",
            "symbol": "KNEIRO/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "KFLOKI/USDC:USDC": {
            "id": "FLOKI",
            "symbol": "KFLOKI/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "KLUNC/USDC:USDC": {
            "id": "LUNC",
            "symbol": "KLUNC/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
        "KBONK/USDC:USDC": {
            "id": "BONK",
            "symbol": "KBONK/USDC:USDC",
            "active": True,
            "quote": "USDC",
            "swap": True,
            "spot": False,
        },
    }


def get_hyperliquid_special_prefix_pairs():
    return [
        "KPEPE/USDC:USDC",
        "KSHIB/USDC:USDC",
        "KNEIRO/USDC:USDC",
        "KFLOKI/USDC:USDC",
        "KLUNC/USDC:USDC",
        "KBONK/USDC:USDC",
    ]


def get_hyperliquid_binance_matches():
    return {
        "KPEPE/USDC:USDC": "1000PEPE/USDT:USDT",
        "KSHIB/USDC:USDC": "1000SHIB/USDT:USDT",
        "BTC/USDC:USDC": "BTC/USDT:USDT",
        "ETH/USDC:USDC": "ETH/USDT:USDT",
        "SOL/USDC:USDC": "SOL/USDT:USDT",
    }


def get_hyperliquid_no_matches():
    return [
        "KPEPE/USDC:USDC",
        "KSHIB/USDC:USDC",
        "KNEIRO/USDC:USDC",
    ]


def get_binance_file_content():
    return """BINANCE:BTCUSDTPERP
BINANCE:ETHUSDTPERP
BINANCE:SOLUSDTPERP
BINANCE:1000PEPEUSDTPERP
BINANCE:XRPUSDTPERP
BINANCE:BNBUSDTPERP
BINANCE:USDCUSDTPERP
BINANCE:FDUSDUSDTPERP
"""


def get_binance_file_content_spot():
    return """BINANCE:BTCUSDT
BINANCE:ETHUSDT
BINANCE:USDCUSDT
BINANCE:FDUSDUSDT
"""
