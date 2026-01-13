import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")


@pytest.fixture
def tmp_path():
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_ccxt_exchange():
    exchange = Mock()
    exchange.load_markets = Mock(return_value={})
    return exchange


@pytest.fixture
def mock_requests_response():
    response = Mock()
    response.status_code = 200
    response.content = b"test content"
    response.json = Mock(return_value=[])
    return response


@pytest.fixture
def sample_market_data():
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 50000.0,
            "market_cap": 1000000000000,
            "market_cap_rank": 1,
            "total_volume": 30000000000,
            "price_change_24h": 2.5,
            "high_24h": 51000.0,
            "low_24h": 49000.0,
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3000.0,
            "market_cap": 360000000000,
            "market_cap_rank": 2,
            "total_volume": 15000000000,
            "price_change_24h": -1.2,
            "high_24h": 3100.0,
            "low_24h": 2950.0,
        },
        {
            "id": "solana",
            "symbol": "sol",
            "name": "Solana",
            "current_price": 100.0,
            "market_cap": 45000000000,
            "market_cap_rank": 10,
            "total_volume": 2000000000,
            "price_change_24h": 5.0,
            "high_24h": 105.0,
            "low_24h": 95.0,
        },
    ]


@pytest.fixture
def sample_binance_pairs():
    return [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
        "1000PEPE/USDT",
        "XRP/USDT",
        "BNB/USDT",
    ]


@pytest.fixture
def sample_tradingview_pairs():
    return [
        "BINANCE:BTCUSDTPERP",
        "BINANCE:ETHUSDTPERP",
        "BINANCE:SOLUSDTPERP",
        "BINANCE:1000PEPEUSDTPERP",
        "BINANCE:XRPUSDTPERP",
        "BINANCE:BNBUSDTPERP",
    ]


@pytest.fixture
def sample_hyperliquid_pairs():
    return [
        "BTC/USDC",
        "ETH/USDC",
        "SOL/USDC",
        "KPEPE/USDC",
        "KSHIB/USDC",
        "KNEIRO/USDC",
    ]


@pytest.fixture
def binance_markets_swap():
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
        "1000PEPE/USDT:USDT": {
            "id": "PEPEUSDT",
            "symbol": "1000PEPE/USDT:USDT",
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
    }


@pytest.fixture
def binance_markets_spot():
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


@pytest.fixture
def hyperliquid_markets():
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
    }
