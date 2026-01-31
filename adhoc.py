import pandas as pd
import numpy as np
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.data_transform import log_return


'''
sharpe ratio = (Expected Return - Risk Free Rate) / StdDev
'''

days = 252

rf_annual_rate = 0.045

# result

## log_return
portfo_return = {
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    "A": [1, 1, 1, 1],
    "B": [0, 0, 0, 0],
    "C": [-1, -1, -1, -1], 
    "D": [1, 2, 3, 4]
}

portfo_return_df = pd.DataFrame(portfo_return)

allocation_df = pd.DataFrame({
    "Tickers": ["A", "B", "C", "D"],
    "Allocation Percentage": [70, 5, 10, 15],
})

# result

result = portfo_metrics(
    portfo_return_df, 
    allocation_df, 
    trading_days=days, 
    rf_annual_rate=rf_annual_rate
    )['Sharpe Ratio']

# expected
## implementation of daily risk-free log return
portfo_retrun_weighted = {
    'Date': portfo_return_df['Date'], 
    'A': portfo_return_df['A']*0.7,
    'B': portfo_return_df['B']*0.05,
    'C': portfo_return_df['C']*0.1,
    'D': portfo_return_df['D']*0.15
}


rf_daily_rate = (1 + rf_annual_rate)**(1/days) - 1
rf_daily_log = np.log1p(rf_daily_rate)

portfo_return_weighted_df = pd.DataFrame(portfo_retrun_weighted)

portfo_return_weighted_df['Portfolio'] = (
    portfo_return_weighted_df
    .drop(columns=['Date'])
    .sum(axis=1)
)

weighted_return = portfo_return_weighted_df['Portfolio']

excess_lr = weighted_return - rf_daily_log

mu_excess = excess_lr.mean() * days

print(rf_daily_rate)