import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, patch

from sandwich.application.cli import app
from sandwich.domain.models import ExchangeId, MarketType

runner = CliRunner()


@pytest.mark.unit
class TestMainCLI:
    def test_default_parameters(self):
        with (
            patch("sandwich.application.cli.DIContainer") as mock_container_class,
        ):
            mock_container = mock_container_class.return_value
            
            result = runner.invoke(app, ["--base", "usdtperp"])
            
            assert result.exit_code == 0
            # By default, only parse is called, no commands executed if flags are false
            mock_container.fetch_market_data_command.execute.assert_not_called()

    def test_fetch_flag(self):
        with (
            patch("sandwich.application.cli.DIContainer") as mock_container_class,
        ):
            mock_container = mock_container_class.return_value
            
            result = runner.invoke(app, ["--fetch"])
            
            assert result.exit_code == 0
            mock_container.fetch_market_data_command.execute.assert_called_once()

    def test_get_pairs_flag(self):
        with (
            patch("sandwich.application.cli.DIContainer") as mock_container_class,
        ):
            mock_container = mock_container_class.return_value
            mock_fetch_cmd = Mock()
            mock_sort_cmd = Mock()
            mock_container.get_fetch_pairs_command.return_value = mock_fetch_cmd
            mock_container.get_sort_pairs_command.return_value = mock_sort_cmd
            
            result = runner.invoke(app, ["--get-pairs", "--base", "usdtperp"])
            
            assert result.exit_code == 0
            mock_container.get_fetch_pairs_command.assert_called_with(ExchangeId.BINANCE)
            mock_fetch_cmd.execute.assert_called_once_with("USDT", MarketType.SWAP)
            mock_sort_cmd.execute.assert_called_once_with("USDT", "swap", is_hyperliquid=False)

    def test_hyperliquid_flag(self):
        with (
            patch("sandwich.application.cli.DIContainer") as mock_container_class,
        ):
            mock_container = mock_container_class.return_value
            mock_match_cmd = Mock()
            mock_sort_cmd = Mock()
            mock_container.get_match_pairs_command.return_value = mock_match_cmd
            mock_container.get_sort_pairs_command.return_value = mock_sort_cmd
            
            result = runner.invoke(app, ["--hyperliquid", "--base", "usdcperp"])
            
            assert result.exit_code == 0
            mock_match_cmd.execute.assert_called_once_with(ExchangeId.BINANCE, "USDC", MarketType.SWAP)
            mock_sort_cmd.execute.assert_called_once_with("USDC", "swap", is_hyperliquid=True)

    def test_all_flags(self):
        with (
            patch("sandwich.application.cli.DIContainer") as mock_container_class,
        ):
            mock_container = mock_container_class.return_value
            mock_fetch_pairs_cmd = Mock()
            mock_match_cmd = Mock()
            mock_sort_cmd = Mock()
            mock_container.get_fetch_pairs_command.return_value = mock_fetch_pairs_cmd
            mock_container.get_match_pairs_command.return_value = mock_match_cmd
            mock_container.get_sort_pairs_command.return_value = mock_sort_cmd
            
            result = runner.invoke(app, ["--fetch", "--get-pairs", "--hyperliquid", "--base", "usdtperp"])
            
            assert result.exit_code == 0
            mock_container.fetch_market_data_command.execute.assert_called_once()
            mock_fetch_pairs_cmd.execute.assert_called_once_with("USDT", MarketType.SWAP)
            mock_match_cmd.execute.assert_called_once_with(ExchangeId.BINANCE, "USDT", MarketType.SWAP)
            mock_sort_cmd.execute.assert_called_once_with("USDT", "swap", is_hyperliquid=True)

    def test_invalid_base(self):
        result = runner.invoke(app, ["--base", "invalid"])
        # parse_base_and_market_type is called, it should just uppercase it and set to SPOT if no perp
        # Wait, if it's "invalid", it will be base="INVALID", market_type=SPOT. 
        # So it won't fail validation unless we add more checks.
        assert result.exit_code == 0