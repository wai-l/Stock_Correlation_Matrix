import pandas as pd
import numpy as np

from .stock_api import ticker_closed_price


def main(): 
    tickers = ["AAPL", "MSFT", "NVDA", "BARC.L"]
    start_date = "2025-01-09"
    end_date = "2025-01-30"

    df = ticker_closed_price(tickers, start_date, end_date)

    # --- create your normalised copy ---
    closed_price_norm = normalize_to_100(df, date_col="Date", base=100)

    log_retuirn_df = log_return(df, date_col="Date")

    print('Raw')
    print(df)
    print('------------------')
    print('Indexed')
    print(closed_price_norm)
    print('------------------')
    print('Log Return')
    print(log_retuirn_df)

def log_return(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    out = df.copy()
    price_cols = [c for c in out.columns if c != date_col]

    for c in price_cols:
        s = out[c]
        # keep NaNs, but compute returns using last available price
        lr = np.log(s.dropna()).diff()
        out[c] = lr.reindex(out.index)

    return out

def normalize_to_100(
    df: pd.DataFrame,
    date_col: str = "Date",
    base: float = 100.0,
    price_cols: list[str] | None = None
    ) -> pd.DataFrame:
    """
    Normalise each price column to an index starting at `base` using
    the first non-null price in that column within the dataframe.
    """
    out = df.copy()

    # out[date_col] = pd.to_datetime(out[date_col]).dt.date

    # Identify price columns
    if price_cols is None:
        price_cols = [c for c in out.columns if c != date_col]

    # Ensure numeric (Streamlit tables sometimes contain None objects)
    out[price_cols] = out[price_cols].apply(pd.to_numeric, errors="coerce")

    # First non-null value per column (base per ticker)
    first_valid = out[price_cols].apply(lambda s: s.dropna().iloc[0] if s.notna().any() else np.nan)

    # Normalise
    out[price_cols] = out[price_cols].div(first_valid).mul(base)

    return out

if __name__ == "__main__":
    main()