from .download import save_market_data, sort_market_data

def main() -> str:
    save_market_data()
    sort_market_data()
    return "Completed"

