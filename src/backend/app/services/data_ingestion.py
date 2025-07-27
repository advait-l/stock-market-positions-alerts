"""
This service is responsible for ingesting real-time stock market data from a provider.
"""

import indstocks as stocks
import pandas as pd

def fetch_stock_data(ticker: str):
    """
    Fetches real-time stock data for a given ticker using the indstocks library.
    """
    print(f"Fetching data for {ticker}...")
    try:
        quote = stocks.Quote(ticker)
        stock_data = quote.get_all_stock_data()
        return stock_data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Example usage:
    stock_data = fetch_stock_data("RELIANCE")
    if stock_data:
        # Convert to pandas DataFrame for better readability
        df = pd.DataFrame.from_dict(stock_data, orient='index')
        print(df) 