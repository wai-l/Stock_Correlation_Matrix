import pandas as pd
import numpy as np
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.data_transform import log_return


days = 252

# result

## actual price
portfo_return = {
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "A": [100, 200, 300],
    "B": [100, 200, 300]
}

portfo_return_df = pd.DataFrame(portfo_return)

allocation_df = pd.DataFrame({
    "Tickers": ["A", "B"],
    "Allocation Percentage": [50, 50],
})

## log return
log_return_df = log_return(portfo_return_df, 'Date')

result = portfo_metrics(
    log_return_df, 
    allocation_df, 
    trading_days=days
    )['Contribution (log)']

result_2 = portfo_metrics(
    log_return_df, 
    allocation_df, 
    trading_days=days
    )['Contribution']

# expected
expected_ab  = (np.log(300) - np.log(100)) # average log return of A and B
expected  = pd.Series({
    'A': expected_ab * 0.5,
    'B': expected_ab * 0.5
    })

print(result)
print(expected)

print(result_2)

print(np.exp(result))

print('-'*50)
# normal cum contribution cal
normal = (300-100)/100 * 0.5

log_exp = np.exp((np.log(300) - np.log(100)) * 0.5)

print(normal)
print(log_exp)