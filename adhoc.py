import pandas as pd
import numpy as np
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.data_transform import log_return

days = 252

# actual price
portfo_return = {
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    "A": [0, 0, 0, 0]
}

portfo_return_df = pd.DataFrame(portfo_return)

log_return_df = log_return(portfo_return_df)

allocation_df = pd.DataFrame({
    "Tickers": ["A"],
    "Allocation Percentage": [70],
})

result = portfo_metrics(log_return_df, allocation_df, trading_days=days)['Expected Return (μ)']

print(result)