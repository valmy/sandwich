import typer
from .coingecko.markets import save_market_data
from .binance.pairs import get_and_save_pairs
from .hyperliquid.pairs import get_and_save_hyperliquid_pairs
from .process import sort_market_data

app = typer.Typer()

@app.command()
def main(base: str = 'usdtperp', fetch: bool = False, get_pairs: bool = False, hyperliquid: bool = False):
    if base.lower().endswith('perp'):
        base_currency = base[:-4].upper()
        market_type = 'swap'
    else:
        base_currency = base.upper()
        market_type = 'spot'

    if fetch:
        save_market_data()

    if get_pairs and not hyperliquid:
        get_and_save_pairs(base_currency, market_type)

    if hyperliquid:
        get_and_save_hyperliquid_pairs(base_currency, 'USDT', market_type)
        # If we've fetched hyperliquid pairs, sort them as well
        sort_market_data('USDT', market_type, is_hyperliquid=True)

    # Sort the regular pairs (if hyperliquid wasn't specified)
    if not hyperliquid or get_pairs:
        sort_market_data(base_currency, market_type)

    print(f"Completed: {base} Fetch: {fetch} Get Pairs: {get_pairs} Hyperliquid: {hyperliquid}")

if __name__ == "__main__":
    app()
