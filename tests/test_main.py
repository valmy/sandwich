import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, patch

runner = CliRunner()


@pytest.mark.unit
class TestMainCLI:
    def test_default_parameters(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.application.container.DIContainer") as mock_container,
            patch("sandwich.application.commands.FetchMarketDataCommand"),
            patch("sandwich.application.commands.FetchPairsCommand"),
            patch("sandwich.application.commands.MatchPairsCommand"),
            patch("sandwich.application.commands.SortPairsCommand"),
        ):
            main(base="usdtperp", fetch=False, get_pairs=False, hyperliquid=False)

            captured = capsys.readouterr()
            # No stdout output expected (relying on logger)
            assert captured.out == ""

    def test_perp_suffix_parsing(self):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            main(base="usdtperp", fetch=False, get_pairs=True, hyperliquid=False)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "USDT"
            assert call_args[0][1] == "swap"

    def test_no_perp_suffix(self):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            main(base="usdc", fetch=False, get_pairs=True, hyperliquid=False)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "USDC"
            assert call_args[0][1] == "spot"

    def test_fetch_flag_only(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data") as mock_save,
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            main(base="usdtperp", fetch=True, get_pairs=False, hyperliquid=False)

            mock_save.assert_called_once()
            captured = capsys.readouterr()
            assert "Fetch: True" in captured.out

    def test_get_pairs_only(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            main(base="usdtperp", fetch=False, get_pairs=True, hyperliquid=False)

            mock_get.assert_called_once()
            captured = capsys.readouterr()
            assert "Get Pairs: True" in captured.out

    def test_hyperliquid_flag(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs") as mock_hl,
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdcperp", fetch=False, get_pairs=False, hyperliquid=True)

            mock_hl.assert_called_once()
            assert mock_sort.call_count == 1
            captured = capsys.readouterr()
            assert "Hyperliquid: True" in captured.out

    def test_fetch_and_get_pairs(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data") as mock_save,
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdtperp", fetch=True, get_pairs=True, hyperliquid=False)

            mock_save.assert_called_once()
            mock_get.assert_called_once()
            assert mock_sort.call_count == 1
            captured = capsys.readouterr()
            assert "Fetch: True Get Pairs: True" in captured.out

    def test_fetch_and_hyperliquid(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data") as mock_save,
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs") as mock_hl,
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdcperp", fetch=True, get_pairs=False, hyperliquid=True)

            mock_save.assert_called_once()
            mock_hl.assert_called_once()
            assert mock_sort.call_count == 1
            captured = capsys.readouterr()
            assert "Fetch: True Hyperliquid: True" in captured.out

    def test_get_pairs_and_hyperliquid(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs") as mock_hl,
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdcperp", fetch=False, get_pairs=True, hyperliquid=True)

            mock_get.assert_called_once()
            mock_hl.assert_called_once()
            assert mock_sort.call_count == 2
            captured = capsys.readouterr()
            assert "Get Pairs: True Hyperliquid: True" in captured.out

    def test_all_flags_true(self, capsys):
        from sandwich import main

        with (
            patch("sandwich.save_market_data") as mock_save,
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs") as mock_hl,
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdtperp", fetch=True, get_pairs=True, hyperliquid=True)

            mock_save.assert_called_once()
            assert mock_get.call_count == 0
            mock_hl.assert_called_once()
            assert mock_sort.call_count == 2
            captured = capsys.readouterr()
            assert "Fetch: True Get Pairs: True Hyperliquid: True" in captured.out

    def test_mixed_case_base_currency(self):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            main(base="UsDtPeRp", fetch=False, get_pairs=True, hyperliquid=False)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "USDT"

    def test_uppercase_base_currency_no_perp(self):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            main(base="USDC", fetch=False, get_pairs=True, hyperliquid=False)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "USDC"
            assert call_args[0][1] == "spot"

    def test_hyperliquid_sort_parameters(self):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs") as mock_hl,
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdcperp", fetch=False, get_pairs=False, hyperliquid=True)

            mock_sort.assert_called()
            sort_calls = mock_sort.call_args_list
            assert any(call[1].get("is_hyperliquid") for call in sort_calls)

    def test_regular_sort_when_not_hyperliquid(self):
        from sandwich import main

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data") as mock_sort,
        ):
            main(base="usdtperp", fetch=False, get_pairs=True, hyperliquid=False)

            mock_sort.assert_called_once()
            call_args = mock_sort.call_args
            assert (
                call_args[0][2] is False or call_args[1].get("is_hyperliquid") is False
            )


@pytest.mark.unit
class TestCLIRunner:
    def test_cli_command_exists(self):
        from sandwich import app

        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_cli_default_invocation(self):
        from sandwich import app

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            result = runner.invoke(app, [])
            assert result.exit_code == 0

    def test_cli_with_parameters(self):
        from sandwich import app

        with (
            patch("sandwich.save_market_data") as mock_save,
            patch("sandwich.get_and_save_pairs") as mock_get,
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            result = runner.invoke(
                app, ["--base", "usdtperp", "--fetch", "--get-pairs"]
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()
            mock_get.assert_called_once()

    def test_cli_hyperliquid_flag(self):
        from sandwich import app

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs") as mock_hl,
            patch("sandwich.sort_market_data"),
        ):
            result = runner.invoke(app, ["--base", "usdcperp", "--hyperliquid"])

            assert result.exit_code == 0
            mock_hl.assert_called_once()

    def test_cli_output_verification(self):
        from sandwich import app

        with (
            patch("sandwich.save_market_data"),
            patch("sandwich.get_and_save_pairs"),
            patch("sandwich.get_and_save_hyperliquid_pairs"),
            patch("sandwich.sort_market_data"),
        ):
            result = runner.invoke(app, ["--base", "usdtperp"])

            assert "Completed:" in result.stdout
            assert "usdtperp" in result.stdout

    def test_hyperliquid_currency_equivalence(self, tmp_path):
        """Test that USDC ↔ USDT currency equivalence works when matching"""
        from pathlib import Path
        from sandwich.application.container import DIContainer
        from sandwich.domain.models import ExchangeId, MarketType

        # Create Binance USDT pairs file
        binance_file = tmp_path / "usdt_swap_pairs.txt"
        binance_file.write_text(
            "BINANCE:BTCUSDTPERP\nBINANCE:ETHUSDTPERP\nBINANCE:SOLUSDTPERP\n"
        )

        # Create Hyperliquid USDC pairs file
        hl_file = tmp_path / "usdc_swap_pairs.txt"
        hl_file.write_text(
            "HYPERLIQUID:BTCUSDCPERP\nHYPERLIQUID:ETHUSDCPERP\nHYPERLIQUID:SOLUSDCPERP\n"
        )

        # Run matching
        container = DIContainer(data_dir=tmp_path)
        match_cmd = container.get_match_pairs_command()
        result = match_cmd.execute(ExchangeId.BINANCE, "USDT", MarketType.SWAP)

        # Verify that 3 pairs matched (BTC, ETH, SOL)
        assert len(result) == 3
        assert "BINANCE:BTCUSDTPERP" in result
        assert "BINANCE:ETHUSDTPERP" in result
        assert "BINANCE:SOLUSDTPERP" in result

        # Verify output file exists and has BINANCE prefix
        hype_file = tmp_path / "usdt_swap_hype_pairs.txt"
        assert hype_file.exists()
        content = hype_file.read_text()
        assert "BINANCE:BTCUSDTPERP" in content
        assert "BINANCE:ETHUSDTPERP" in content
        assert "BINANCE:SOLUSDTPERP" in content
        # Ensure no HYPERLIQUID prefix in output
        assert "HYPERLIQUID:" not in content
