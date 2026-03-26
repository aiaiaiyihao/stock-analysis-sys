import yfinance as yf


def fetch_stock_data(symbol: str, period: str = "1mo"):
    df = yf.download(symbol, period=period, interval="1d", auto_adjust=False)
    if df.empty:
        raise ValueError(f"No data found for symbol: {symbol}")
    return df