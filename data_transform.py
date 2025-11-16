import pandas as pd
import numpy as np

def log_return(df):
    """
    Calculate the log return of stock prices.

    Parameters:
    df (pd.DataFrame): DataFrame containing stock prices with 'Date' column.

    Returns:
    pd.DataFrame: DataFrame with log returns.

    Logic: 
    return = ln(price(n)/price(n-1)) = ln(price(n)) - ln(price(n-1))
    """
    df_returns = df.copy()
    df_returns.iloc[:, 1:] = df_returns.iloc[:, 1:].apply(lambda x: np.log(x) - np.log(x.shift(1)))
    return df_returns