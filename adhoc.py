import pandas as pd
import numpy as np
from app_lib.metrics import asset_metrics
from app_lib.data_transform import log_return

n = pd.DataFrame({
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    'A': [1, -1, 1, -1], 
    'B': [1, 1, 1, 1], 
    'C': [1, 2, 3, 4]
    })

metrics = asset_metrics(n)

a = metrics['Annualised Return (μ)'].reset_index(drop=True)

print(a)

print('='*16)

b = pd.Series([1, 2])

print(b)

print('='*16)

log_exp_df = pd.DataFrame(
    {'x': [0, 1, 2, 3, 4]}
)

log_exp_df['log'] = np.log(log_exp_df['x'])

log_exp_df['exp'] = np.exp(log_exp_df['x'])

print(log_exp_df)

print('='*16)

log_return_df = log_return(n, 'Date')

print(log_return_df)

print('='*16)

result = asset_metrics(log_return_df)

print(result)