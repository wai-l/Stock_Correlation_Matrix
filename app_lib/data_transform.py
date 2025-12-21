import pandas as pd
import numpy as np

# def log_return(price_df: pd.DataFrame, date_col='Date') -> pd.DataFrame:
#     """
#     Calculate daily log returns from price data.

#     Parameters
#     ----------
#     price_df : pd.DataFrame
#         DataFrame with a date column and price columns.
#     date_col : str
#         Name of the date column.

#     Returns
#     -------
#     pd.DataFrame
#         Log return DataFrame with same shape.
#     """
#     df = price_df.copy()

#     price_cols = [c for c in df.columns if c != date_col]

#     # guard against non-positive prices
#     df[price_cols] = df[price_cols].where(df[price_cols] > 0)

#     df[price_cols] = np.log(df[price_cols]).diff()

#     return df

def log_return(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    out = df.copy()
    price_cols = [c for c in out.columns if c != date_col]

    for c in price_cols:
        s = out[c]
        # keep NaNs, but compute returns using last available price
        lr = np.log(s.dropna()).diff()
        out[c] = lr.reindex(out.index)

    return out