from fastapi import APIRouter
from app.services.data_ingestion import fetch_stock_data

router = APIRouter()

STOCKS = ["RELIANCE", "TCS", "HDFCBANK", "INFY"]

@router.get("/stocks")
def get_stocks():
    stock_data = []
    for stock in STOCKS:
        data = fetch_stock_data(stock)
        if data:
            # Add the ticker to the data object for easier identification on the frontend
            data['ticker'] = stock
            stock_data.append(data)
    return stock_data

@router.get("/stocks/{ticker}")
def get_stock_details(ticker: str):
    """
    Fetches detailed information for a single stock.
    """
    return fetch_stock_data(ticker)
