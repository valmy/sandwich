import typer

from .container import DIContainer
from sandwich.domain.models import ExchangeId
from sandwich.domain.validators import parse_base_and_market_type
from sandwich.domain.exceptions import DataValidationError
from sandwich.infrastructure.logging import get_logger

logger = get_logger(__name__)

app = typer.Typer()


@app.command()
def main(
    base: str = "usdtperp",
    fetch: bool = False,
    get_pairs: bool = False,
    exchange: str = typer.Option("binance", "--exchange", "-e", help="Exchange to use"),
) -> None:
    """
    Main CLI command.

    Args:
        base: Base currency and market type (e.g., usdtperp, usdc, fdusd)
        fetch: Fetch market data from CoinGecko
        get_pairs: Get pairs from exchange
        exchange: Exchange to use (binance, hyperliquid, aster, etc.)
    """
    container = DIContainer()

    try:
        # Validate exchange
        try:
            exchange_id = ExchangeId(exchange)
        except ValueError:
            valid_exchanges = [e.value for e in ExchangeId]
            raise typer.BadParameter(
                f"Invalid exchange '{exchange}'. Valid options: {valid_exchanges}"
            )

        base_currency, market_type = parse_base_and_market_type(base)

        logger.info(
            f"Starting: base={base_currency}, type={market_type.value}, "
            f"fetch={fetch}, get_pairs={get_pairs}, exchange={exchange}"
        )

        if fetch:
            container.fetch_market_data_command.execute()

        if get_pairs:
            from sandwich.config.exchanges import get_config

            config = get_config(exchange)

            if "match_with" in config:
                # Exchange needs pair matching against another exchange
                fetch_source_cmd = container.get_fetch_pairs_command(exchange_id)
                fetch_source_cmd.execute(base_currency, market_type)

                match_cmd = container.get_match_pairs_command()
                match_cmd.execute(exchange_id, base_currency, market_type)

                sort_cmd = container.get_sort_pairs_command()
                sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=True)
            else:
                # Exchange stands alone (TradingView-supported)
                fetch_cmd = container.get_fetch_pairs_command(exchange_id)
                fetch_cmd.execute(base_currency, market_type)

                sort_cmd = container.get_sort_pairs_command()
                sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=False)

        # Handle pair matching without fetch (legacy use case)
        if not get_pairs and exchange_id in [ExchangeId.HYPERLIQUID, ExchangeId.ASTER]:
            from sandwich.config.exchanges import get_config

            config = get_config(exchange)
            if "match_with" in config:
                match_cmd = container.get_match_pairs_command()
                match_cmd.execute(exchange_id, base_currency, market_type)

                sort_cmd = container.get_sort_pairs_command()
                sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=True)

        logger.info(
            f"Completed: {base} Fetch: {fetch} Get Pairs: {get_pairs} "
            f"Exchange: {exchange}"
        )

    except DataValidationError as e:
        logger.error(f"Validation error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
