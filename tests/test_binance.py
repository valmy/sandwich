import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from tests.fixtures.binance_fixtures import (
    get_binance_markets_swap,
    get_binance_markets_spot,
    get_binance_empty_markets,
    get_binance_inactive_markets,
    get_binance_usdc_swap_markets,
    get_tradingview_format_pairs_swap,
    get_tradingview_format_pairs_spot,
)


@pytest.mark.unit
class TestGetPairs:
    def test_usdt_swap_pairs(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_markets_swap()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            pairs = get_pairs("USDT", "swap")

            assert len(pairs) == 8
            assert "BTC/USDT:USDT" in pairs
            assert "ETH/USDT:USDT" in pairs
            assert "1000PEPE/USDT:USDT" in pairs
            assert "USDC/USDT:USDT" in pairs
            assert "FDUSD/USDT:USDT" in pairs

    def test_usdc_spot_pairs(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_markets_spot()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            pairs = get_pairs("USDT", "spot")

            assert len(pairs) == 3
            assert "BTC/USDT" in pairs
            assert "ETH/USDT" in pairs
            assert "USDC/USDT" in pairs

    def test_fdusd_swap_pairs(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_usdc_swap_markets()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            pairs = get_pairs("USDC", "swap")

            assert len(pairs) == 2
            assert "BTC/USDC:USDC" in pairs
            assert "ETH/USDC:USDC" in pairs

    def test_empty_result_handling(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_empty_markets()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            pairs = get_pairs("USDT", "swap")
            assert len(pairs) == 0

    def test_invalid_base_currency(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_markets_swap()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            pairs = get_pairs("INVALID", "swap")
            assert len(pairs) == 0

    def test_invalid_market_type(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_markets_swap()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            with pytest.raises(KeyError):
                get_pairs("USDT", "invalid")

    def test_inactive_pairs_excluded(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_inactive_markets()

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            pairs = get_pairs("USDT", "swap")
            assert len(pairs) == 0

    def test_api_error_handling(self):
        from sandwich.binance.pairs import get_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.side_effect = Exception("API Error")

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            with pytest.raises(Exception, match="API Error"):
                get_pairs("USDT", "swap")


@pytest.mark.unit
class TestSavePairsForTradingview:
    def test_swap_pairs_format(self, tmp_path, capsys):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"]
        filename = tmp_path / "usdt_swap_pairs.txt"

        save_pairs_for_tradingview(pairs, "USDT", "swap", str(filename))

        captured = capsys.readouterr()
        assert "USDT swap pairs saved to" in captured.out

        with open(filename, "r") as f:
            lines = f.read().strip().split("\n")
            assert lines[0] == "BINANCE:BTCUSDTPERP"
            assert lines[1] == "BINANCE:ETHUSDTPERP"
            assert lines[2] == "BINANCE:SOLUSDTPERP"

    def test_spot_pairs_format(self, tmp_path, capsys):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = ["BTC/USDT", "ETH/USDT"]
        filename = tmp_path / "usdt_spot_pairs.txt"

        save_pairs_for_tradingview(pairs, "USDT", "spot", str(filename))

        captured = capsys.readouterr()
        assert "USDT spot pairs saved to" in captured.out

        with open(filename, "r") as f:
            lines = f.read().strip().split("\n")
            assert lines[0] == "BINANCE:BTCUSDT"
            assert lines[1] == "BINANCE:ETHUSDT"

    def test_default_filename(self, tmp_path, capsys):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = ["BTC/USDT:USDT", "ETH/USDT:USDT"]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            save_pairs_for_tradingview(pairs, "USDT", "swap")

            filename = tmp_path / "usdt_swap_pairs.txt"
            assert filename.exists()

            with open(filename, "r") as f:
                content = f.read()
                assert "BINANCE:BTCUSDTPERP" in content
        finally:
            os.chdir(original_cwd)

    def test_empty_pairs_list(self, tmp_path, capsys):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = []
        filename = tmp_path / "empty_pairs.txt"

        save_pairs_for_tradingview(pairs, "USDT", "swap", str(filename))

        captured = capsys.readouterr()
        assert "USDT swap pairs saved to" in captured.out

        with open(filename, "r") as f:
            content = f.read()
            assert content == ""

    def test_file_write_error(self, tmp_path, capsys):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = ["BTC/USDT:USDT"]
        filename = tmp_path / "readonly" / "pairs.txt"
        (tmp_path / "readonly").mkdir()

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            save_pairs_for_tradingview(pairs, "USDT", "swap", str(filename))

    def test_tradingview_format_correctness(self, tmp_path):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = ["BTC/USDT:USDT", "1000PEPE/USDT:USDT"]
        filename = tmp_path / "format_test.txt"

        save_pairs_for_tradingview(pairs, "USDT", "swap", str(filename))

        with open(filename, "r") as f:
            lines = f.read().strip().split("\n")
            assert all(line.startswith("BINANCE:") for line in lines)
            assert all(line.endswith("PERP") for line in lines)

    def test_binance_prefix_included(self, tmp_path):
        from sandwich.binance.pairs import save_pairs_for_tradingview

        pairs = ["BTC/USDT:USDT"]
        filename = tmp_path / "prefix_test.txt"

        save_pairs_for_tradingview(pairs, "USDT", "swap", str(filename))

        with open(filename, "r") as f:
            content = f.read()
            assert content.startswith("BINANCE:")


@pytest.mark.unit
class TestGetAndSavePairs:
    def test_end_to_end_flow(self, tmp_path, capsys):
        from sandwich.binance.pairs import get_and_save_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = get_binance_markets_swap()

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch(
                "sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange
            ):
                get_and_save_pairs("USDT", "swap")

                captured = capsys.readouterr()
                assert "Getting USDT swap pairs..." in captured.out
                assert "USDT swap pairs: 8 found" in captured.out
                assert "USDT swap pairs saved to" in captured.out

                filename = tmp_path / "usdt_swap_pairs.txt"
                assert filename.exists()
        finally:
            os.chdir(original_cwd)

    def test_error_propagation(self, tmp_path, capsys):
        from sandwich.binance.pairs import get_and_save_pairs

        mock_exchange = Mock()
        mock_exchange.load_markets.side_effect = Exception("API Error")

        with patch("sandwich.binance.pairs.ccxt.binance", return_value=mock_exchange):
            with pytest.raises(Exception, match="API Error"):
                get_and_save_pairs("USDT", "swap")
