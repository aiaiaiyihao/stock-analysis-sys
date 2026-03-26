def add_indicators(df):
    df = df.copy()
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["Daily_Return"] = df["Close"].pct_change()
    return df