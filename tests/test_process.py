import pytest
import json
from pathlib import Path
from tests.fixtures.coingecko_fixtures import get_coingecko_market_data


@pytest.mark.unit
class TestRemovePrefixSuffix:
    def test_remove_binance_prefix(self):
        from sandwich.process import remove_prefix_suffix

        result = remove_prefix_suffix("BINANCE:BTCUSDTPERP")
        assert result == "BTCUSDT"

    def test_remove_perp_suffix(self):
        from sandwich.process import remove_prefix_suffix

        result = remove_prefix_suffix("BTCUSDTPERP")
        assert result == "BTCUSDT"

    def test_remove_both_prefix_and_suffix(self):
        from sandwich.process import remove_prefix_suffix

        result = remove_prefix_suffix("BINANCE:BTCUSDTPERP")
        assert result == "BTCUSDT"

    def test_no_prefix_or_suffix(self):
        from sandwich.process import remove_prefix_suffix

        result = remove_prefix_suffix("BTCUSDT")
        assert result == "BTCUSDT"

    def test_multiple_binance_occurrences(self):
        from sandwich.process import remove_prefix_suffix

        result = remove_prefix_suffix("BINANCE:BINANCE:BTCUSDTPERP")
        assert result == "BINANCE:BTCUSDT"

    def test_perp_in_middle_of_string(self):
        from sandwich.process import remove_prefix_suffix

        result = remove_prefix_suffix("PERPETUALUSDT")
        assert result == "PERPETUALUSDT"


@pytest.mark.unit
class TestFindSymbolInLines:
    def test_exact_symbol_match_found(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "btc", "total_volume": 1000000}
        lines = ["BINANCE:BTCUSDTPERP", "BINANCE:ETHUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDT")
        assert result == "BINANCE:BTCUSDTPERP"

    def test_1000_prefix_match(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "pepe", "total_volume": 1000000}
        lines = ["BINANCE:1000PEPEUSDTPERP", "BINANCE:ETHUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDT")
        assert result == "BINANCE:1000PEPEUSDTPERP"

    def test_excluded_currencies_not_matched(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "usdc", "total_volume": 1000000}
        lines = ["BINANCE:USDCUSDTPERP", "BINANCE:USDTUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDT")
        assert result == ""

    def test_symbol_not_found(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "doge", "total_volume": 1000000}
        lines = ["BINANCE:BTCUSDTPERP", "BINANCE:ETHUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDT")
        assert result == ""

    def test_multiple_matches_returns_first(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "btc", "total_volume": 1000000}
        lines = ["BINANCE:BTCUSDTPERP", "BINANCE:BTCUSDT", "BINANCE:ETHUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDT")
        assert result == "BINANCE:BTCUSDTPERP"

    def test_case_insensitive_matching(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "BTC", "total_volume": 1000000}
        lines = ["BINANCE:BTCUSDTPERP", "BINANCE:ETHUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDT")
        assert result == "BINANCE:BTCUSDTPERP"

    def test_base_currency_variations(self):
        from sandwich.process import find_symbol_in_lines

        item = {"symbol": "btc", "total_volume": 1000000}
        lines = ["BINANCE:BTCUSDCPERP", "BINANCE:BTCUSDTPERP"]

        result = find_symbol_in_lines(item, lines, "USDC")
        assert result == "BINANCE:BTCUSDCPERP"


@pytest.mark.unit
class TestSortMarketData:
    def test_regular_pairs_sorting(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = [
            {"symbol": "eth", "total_volume": 15000000000},
            {"symbol": "btc", "total_volume": 45339514765},
            {"symbol": "sol", "total_volume": 2000000000},
        ]

        pairs_lines = [
            "BINANCE:BTCUSDTPERP",
            "BINANCE:ETHUSDTPERP",
            "BINANCE:SOLUSDTPERP",
            "BINANCE:DOGEUSDTPERP",
        ]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open("marketcap.json", "w") as f:
                json.dump(market_data, f)

            with open("usdt_swap_pairs.txt", "w") as f:
                f.write("\n".join(pairs_lines))

            sort_market_data("USDT", "swap", is_hyperliquid=False)

            captured = capsys.readouterr()
            assert "3 lines" in captured.out
            assert "Number of unsorted symbols: 1" in captured.out

            with open("sorted_usdt_swap.txt", "r") as f:
                sorted_lines = f.read().strip().split("\n")
                assert sorted_lines[0] == "BINANCE:BTCUSDTPERP"
                assert sorted_lines[1] == "BINANCE:ETHUSDTPERP"
                assert sorted_lines[2] == "BINANCE:SOLUSDTPERP"
                assert sorted_lines[3] == "BINANCE:DOGEUSDTPERP"
        finally:
            os.chdir(original_cwd)

    def test_hyperliquid_pairs_sorting(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = [
            {"symbol": "eth", "total_volume": 15000000000},
            {"symbol": "btc", "total_volume": 45339514765},
        ]

        pairs_lines = ["BINANCE:BTCUSDTPERP", "BINANCE:ETHUSDTPERP"]

        txt_file = tmp_path / "usdt_swap_hype_pairs.txt"

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open(txt_file, "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=True)

                captured = capsys.readouterr()
                assert "2 lines" in captured.out

                assert sorted_file.exists()
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_volume_descending_order(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = [
            {"symbol": "sol", "total_volume": 2000000000},
            {"symbol": "eth", "total_volume": 15000000000},
            {"symbol": "btc", "total_volume": 45339514765},
        ]

        pairs_lines = [
            "BINANCE:SOLUSDTPERP",
            "BINANCE:ETHUSDTPERP",
            "BINANCE:BTCUSDTPERP",
        ]

        txt_file = tmp_path / "usdt_swap_pairs.txt"

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open(txt_file, "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)

                with open(sorted_file, "r") as f:
                    sorted_lines = f.read().strip().split("\n")
                    assert sorted_lines[0] == "BINANCE:BTCUSDTPERP"
                    assert sorted_lines[1] == "BINANCE:ETHUSDTPERP"
                    assert sorted_lines[2] == "BINANCE:SOLUSDTPERP"
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_all_symbols_sorted_zero_unsorted(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = [
            {"symbol": "btc", "total_volume": 45339514765},
            {"symbol": "eth", "total_volume": 15000000000},
        ]

        pairs_lines = ["BINANCE:BTCUSDTPERP", "BINANCE:ETHUSDTPERP"]

        txt_file = tmp_path / "usdt_swap_pairs.txt"

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open(txt_file, "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)

                captured = capsys.readouterr()
                assert "Number of unsorted symbols: 0" in captured.out
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_all_symbols_unsorted_zero_sorted(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = [{"symbol": "btc", "total_volume": 45339514765}]

        pairs_lines = ["BINANCE:ETHUSDTPERP", "BINANCE:SOLUSDTPERP"]

        txt_file = tmp_path / "usdt_swap_pairs.txt"

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open(txt_file, "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)

                captured = capsys.readouterr()
                assert "0 lines" in captured.out
                assert "Number of unsorted symbols: 2" in captured.out

                with open(sorted_file, "r") as f:
                    lines = f.read().strip().split("\n")
                    assert "ETHUSDTPERP" in lines[0]
                    assert "SOLUSDTPERP" in lines[1]
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_file_doesnt_exist_marketcap(self, tmp_path):
        from sandwich.process import sort_market_data

        txt_file = tmp_path / "usdt_swap_pairs.txt"
        with open(txt_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(FileNotFoundError):
                sort_market_data("USDT", "swap", is_hyperliquid=False)
        finally:
            os.chdir(original_cwd)

    def test_file_doesnt_exist_pairs(self, tmp_path):
        from sandwich.process import sort_market_data

        market_data = [{"symbol": "btc", "total_volume": 45339514765}]

        with open(json_file, "w") as f:
            json.dump(market_data, f)

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(FileNotFoundError):
                sort_market_data("USDT", "swap", is_hyperliquid=False)
        finally:
            os.chdir(original_cwd)

    def test_malformed_json(self, tmp_path):
        from sandwich.process import sort_market_data

        with open(json_file, "w") as f:
            f.write("invalid json")

        txt_file = tmp_path / "usdt_swap_pairs.txt"
        with open(txt_file, "w") as f:
            f.write("BINANCE:BTCUSDTPERP\n")

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(json.JSONDecodeError):
                sort_market_data("USDT", "swap", is_hyperliquid=False)
        finally:
            os.chdir(original_cwd)

    def test_empty_market_data(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = []
        pairs_lines = ["BINANCE:BTCUSDTPERP"]

        txt_file = tmp_path / "usdt_swap_pairs.txt"

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open(txt_file, "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)

                captured = capsys.readouterr()
                assert "0 lines" in captured.out
                assert "Number of unsorted symbols: 1" in captured.out
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_empty_pairs_list(self, tmp_path, capsys):
        from sandwich.process import sort_market_data

        market_data = [{"symbol": "btc", "total_volume": 45339514765}]
        pairs_lines = []

        txt_file = tmp_path / "usdt_swap_pairs.txt"

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open(txt_file, "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)

                captured = capsys.readouterr()
                assert "0 lines" in captured.out
                assert "Number of unsorted symbols: 0" in captured.out
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_correct_filename_generation(self, tmp_path):
        from sandwich.process import sort_market_data

        market_data = [{"symbol": "btc", "total_volume": 45339514765}]
        pairs_lines = ["BINANCE:BTCUSDTPERP"]


        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open("usdt_swap_pairs.txt", "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)
                assert (tmp_path / "sorted_usdt_swap.txt").exists()

                sort_market_data("USDC", "swap", is_hyperliquid=True)
                assert (tmp_path / "sorted_usdc_swap_hype.txt").exists()
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)

    def test_file_write_success(self, tmp_path):
        from sandwich.process import sort_market_data

        market_data = [{"symbol": "btc", "total_volume": 45339514765}]
        pairs_lines = ["BINANCE:BTCUSDTPERP"]


        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with open(json_file, "w") as f:
                json.dump(market_data, f)

            with open("usdt_swap_pairs.txt", "w") as f:
                f.write("\n".join(pairs_lines))

            import sandwich.process


            try:
                sort_market_data("USDT", "swap", is_hyperliquid=False)
                assert sorted_file.exists()

                with open(sorted_file, "r") as f:
                    content = f.read()
                    assert "BINANCE:BTCUSDTPERP" in content
            finally:
                sandwich.process.json_file = original_json_file
        finally:
            os.chdir(original_cwd)
