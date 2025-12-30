import numpy as np
import pandas as pd
from datetime import date

from .stock_api import ticker_closed_price
from .data_transform import log_return

def main(): 
    # Example usage
    port_allocation = pd.DataFrame(
        {
            "Tickers": ['AAPL', 'TSLA', 'BARC.L', 'VOO', 'QQQ', 'GLD', 'USDGBP=X'],
            "Allocation Percentage": [15, 15, 10, 20, 20, 10, 10]
            }
            )
    tickers = port_allocation['Tickers'].to_list()
    start_date = '2024-12-14'
    end_date = '2025-12-14'

    start_date = date.today().replace(year = date.today().year-1)
    end_date = date.today()


    # Fetch closing prices
    price_df = ticker_closed_price(tickers, start_date, end_date)

    # Calculate log returns
    log_return_df = log_return(price_df)

    asset_m = asset_metrics(log_return_df)

    print(asset_m)
    
    portfo_m = portfo_metrics(log_return_df, port_allocation)

    for i in portfo_m: 
        print(f"{i}: {portfo_m[i]}")




def asset_metrics(
    log_returns: pd.DataFrame,
    date_col: str = "Date",
    trading_days: int = 252
    ) -> pd.DataFrame:
    """
    Compute per-asset performance metrics from daily log returns.

    Parameters
    ----------
    log_returns : pd.DataFrame
        DataFrame with a date column and asset log-return columns.
    date_col : str
        Name of the date column.

    Returns
    -------
    pd.DataFrame
        Asset-level metrics:
        - Annualised Return (μ)
        - Annualised Volatility (σ)
        - Cumulative Return
        - Observations
    """

    r = log_returns.copy()

    # Move date to index if present
    if date_col in r.columns:
        r = r.set_index(date_col)

    ticker_order = r.columns.tolist()


    # Drop assets with no data at all
    r = r.dropna(axis=1, how="all")

    # Core statistics
    annual_return = r.mean() * trading_days
    annual_std = r.std(ddof=1) * np.sqrt(trading_days)

    # Cumulative return from log returns
    cumulative_return = np.exp(r.sum()) - 1

    # Observation count
    obs = r.count()

    metrics = pd.DataFrame(
        {
            "Annualised Return (μ)": annual_return,
            "StdDev (Volatility σ)": annual_std,
            "Cumulative Return": cumulative_return,
            "Observations": obs,
        }
    )

    metrics = metrics.reindex(ticker_order)

    return metrics

def portfo_metrics(log_return_df: pd.DataFrame, 
                   allocation_df: pd.DataFrame, 
                   trading_days: int = 252, 
                   rf_annual_rate: float = 0.045
                   ) -> dict: 
    # weights
    weights = (
        allocation_df
        .set_index('Tickers')['Allocation Percentage']
        .astype(float) / 100
    )
    weights = weights / weights.sum()

    # get daily risk-free ratio
    rf_daily_rate = (1 + rf_annual_rate) ** (1 / trading_days) - 1
    rf_daily_log = np.log1p(rf_daily_rate)

    # align data
    lr = log_return_df[weights.index].dropna()

    
    # per-asset contribution
    daily_contrib = lr.mul(weights, axis=1)
    cumulative_contrib_log = daily_contrib.sum()
    simple_contrib = np.expm1(cumulative_contrib_log)
    contrib_share = cumulative_contrib_log / cumulative_contrib_log.sum()
    cum_contrib_log_sum = cumulative_contrib_log.sum() # for check




    ## weighted log return
    port_lr = lr.mul(weights, axis=1).sum(axis=1)
    ## excess log return
    excess_lr = port_lr - rf_daily_log

    # annualised stats
    mu = port_lr.mean() * trading_days
    mu_excess = excess_lr.mean() * trading_days
    sigma = port_lr.std(ddof=1) * np.sqrt(trading_days)
    sharpe = mu_excess / sigma if sigma > 0 else np.nan

    # cumulative stats
    growth = np.expm1(port_lr.cumsum())
    running_max = growth.cummax()
    drawdown = growth / running_max - 1
    max_dd = drawdown.min()
    cum_return_log = port_lr.sum() # for check
    cum_return = np.exp(port_lr.sum()) - 1

    


    return {
        "Expected Return (μ)": mu,
        "StdDev (Volatility σ)": sigma,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd, 
        "Cumulative Return": cum_return, 
        "Contribution (log)": cumulative_contrib_log,
        "Contribution": simple_contrib,
        "Contribution Share": contrib_share, 

        # for error check
        "Cumulative Return (Log)": cum_return_log, 
        "Cumulative Contribution (Log) Sum": cum_contrib_log_sum, 
        "Diff": cum_return_log - cum_contrib_log_sum

    }


if __name__ == "__main__":
    main()