import typer
from .coingecko.markets import save_market_data
from .binance.pairs import get_and_save_pairs
from .process import sort_market_data

app = typer.Typer()

@app.command()
def main(base: str = 'usdtperp', fetch: bool = False, get_pairs: bool = False):
    if base.lower().endswith('perp'):
        base_currency = base[:-4].upper()
        market_type = 'swap'
    else:
        base_currency = base.upper()
        market_type = 'spot'

    if fetch:
        save_market_data()

    if get_pairs:
        get_and_save_pairs(base_currency, market_type)

    sort_market_data(base_currency, market_type)
    print(f"Completed: {base} Fetch:  {fetch} Get Pairs: {get_pairs}")

if __name__ == "__main__":
    app()
