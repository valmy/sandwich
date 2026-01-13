import typer
from typing import Optional

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
    hyperliquid: bool = False,
    target_base: Optional[str] = None,
) -> None:
    """
    Main CLI command.

    Args:
        base: Base currency and market type (e.g., usdtperp, usdc, fdusd)
        fetch: Fetch market data from CoinGecko
        get_pairs: Get pairs from exchange
        hyperliquid: Use Hyperliquid exchange
        target_base: Target base currency for matching (default: same as base)
    """
    try:
        container = DIContainer()

        base_currency, market_type = parse_base_and_market_type(base)

        logger.info(
            f"Starting: base={base_currency}, type={market_type.value}, "
            f"fetch={fetch}, get_pairs={get_pairs}, hyperliquid={hyperliquid}, "
            f"target_base={target_base}"
        )

        if fetch:
            container.fetch_market_data_command.execute()

        if get_pairs:
            if hyperliquid:
                fetch_hl_cmd = container.get_fetch_pairs_command(ExchangeId.HYPERLIQUID)
                fetch_hl_cmd.execute(base_currency, market_type)

                match_cmd = container.get_match_pairs_command()
                match_cmd.execute(ExchangeId.BINANCE, base_currency, market_type)

                sort_cmd = container.get_sort_pairs_command()
                sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=True)
            else:
                fetch_bn_cmd = container.get_fetch_pairs_command(ExchangeId.BINANCE)
                fetch_bn_cmd.execute(base_currency, market_type)

                sort_cmd = container.get_sort_pairs_command()
                sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=False)

        if hyperliquid and not get_pairs:
            match_cmd = container.get_match_pairs_command()
            match_cmd.execute(ExchangeId.BINANCE, base_currency, market_type)

            sort_cmd = container.get_sort_pairs_command()
            sort_cmd.execute(base_currency, market_type.value, is_hyperliquid=True)

        logger.info(
            f"Completed: {base} Fetch: {fetch} Get Pairs: {get_pairs} "
            f"Hyperliquid: {hyperliquid}"
        )
        print(
            f"Completed: {base} Fetch: {fetch} Get Pairs: {get_pairs} "
            f"Hyperliquid: {hyperliquid}"
        )

    except DataValidationError as e:
        logger.error(f"Validation error: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
