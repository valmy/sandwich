import typer

from .container import DIContainer
from sandwich.config.exchanges import get_config
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

        config = get_config(exchange)
        needs_matching = "match_with" in config

        # Fetch pairs if requested
        if get_pairs:
            fetch_cmd = container.get_fetch_pairs_command(exchange_id)
            fetch_cmd.execute(base_currency, market_type)

        # Handle matching (with or without fetch)
        if needs_matching:
            match_cmd = container.get_match_pairs_command()
            match_cmd.execute(exchange_id, base_currency, market_type)
            sort_cmd = container.get_sort_pairs_command()
            sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=True)
        elif get_pairs:
            # Only sort for non-matching exchanges when fetch was done
            sort_cmd = container.get_sort_pairs_command()
            sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=False)

        logger.info(
            f"Completed: {base} Fetch: {fetch} Get Pairs: {get_pairs} "
            f"Exchange: {exchange}"
        )

    except typer.BadParameter:
        # Let typer handle bad parameter errors
        raise
    except DataValidationError as e:
        logger.error(f"Validation error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
