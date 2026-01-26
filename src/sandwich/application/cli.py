import typer

from .container import DIContainer
from .output import OutputFormat, OutputFormatter
from sandwich.config.exchanges import get_config
from sandwich.domain.models import ExchangeId
from sandwich.domain.validators import parse_base_and_market_type
from sandwich.domain.exceptions import ValidationError
from sandwich.infrastructure.logging import get_logger

logger = get_logger(__name__)

app = typer.Typer()


@app.command()
def main(
    base: str = typer.Option(
        "usdtperp",
        "--base",
        "-b",
        help=(
            "Base currency and market type combined. For swap/perpetual markets, "
            "append 'perp' to the base currency. For spot markets, use just the "
            "currency code. Examples:\n"
            "  - 'usdtperp' = USDT base currency, swap/perpetual market\n"
            "  - 'usdc' = USDC base currency, spot market\n"
            "  - 'fdusdperp' = FDUSD base currency, swap/perpetual market"
        ),
    ),
    fetch: bool = typer.Option(
        False,
        "--fetch",
        "-f",
        help=(
            "Fetch latest market data (price, volume, market cap) from CoinGecko API. "
            "This data is used for sorting pairs by metrics like market cap or volume."
        ),
    ),
    get_pairs: bool = typer.Option(
        False,
        "--get-pairs",
        "-g",
        help=(
            "Fetch and update trading pairs from the specified exchange. "
            "Pairs are filtered by the base currency and market type, "
            "and only active markets are included."
        ),
    ),
    exchange: str = typer.Option(
        "binance",
        "--exchange",
        "-e",
        help=(
            "Exchange to use for fetching pairs. Supported exchanges:\n"
            "  - binance: Binance exchange (default)\n"
            "  - hyperliquid: Hyperliquid exchange (filters pairs against Binance)\n"
            "  - aster: Aster exchange (filters pairs against Binance)\n"
            "Note: Exchanges with 'match_with' configuration will filter pairs "
            "against the specified exchange's pairs."
        ),
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--output",
        "-o",
        help=(
            "Output format. Supported formats:\n"
            "  - text: Plain text output (default)\n"
            "  - json: Structured JSON output"
        ),
    ),
) -> None:
    """
    CLI application to manage TradingView-compatible cryptocurrency trading pair lists.

    This application fetches trading pairs from supported exchanges, matches them
    across platforms (when configured), and sorts them by market metrics (market cap,
    volume) using CoinGecko data.

    Main Features:
        - Fetch and update trading pairs from exchanges
        - Match pairs across exchanges (e.g., Hyperliquid pairs matching Binance)
        - Sort pairs by market cap or volume
        - Fetch and update market data from CoinGecko
        - Generate TradingView-compatible watchlists

    Examples:
        Fetch and update Binance USDT perpetual pairs:
        $ uv run sandwich --base usdtperp --get-pairs

        Fetch and update Hyperliquid USDC perpetual pairs:
        $ uv run sandwich --base usdcperp --get-pairs --exchange hyperliquid

        Only sort existing USDT perpetual pairs by volume:
        $ uv run sandwich --base usdtperp

        Fetch market data and update pairs:
        $ uv run sandwich --fetch --get-pairs
    """
    container = DIContainer()
    formatter = OutputFormatter(output)

    success_data = None

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

        if output == OutputFormat.JSON:
            success_data = {
                "base": base,
                "exchange": exchange,
                "fetch": fetch,
                "get_pairs": get_pairs,
                "message": "Operation completed successfully",
            }

    except typer.BadParameter:
        # Let typer handle bad parameter errors
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        if output == OutputFormat.JSON:
            # Sanitize error message for JSON output to prevent information disclosure
            safe_message = "Invalid input parameters provided"
            typer.echo(formatter.format_error(Exception(safe_message), "Validation failed"))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if output == OutputFormat.JSON:
            # Generic error message to prevent information disclosure
            safe_message = "An internal error occurred"
            typer.echo(formatter.format_error(Exception(safe_message), "Operation failed"))
        raise typer.Exit(code=1)

    if success_data and output == OutputFormat.JSON:
        typer.echo(formatter.format_success(success_data))


if __name__ == "__main__":
    app()
