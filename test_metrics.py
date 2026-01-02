import pandas as pd
import pytest
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.data_transform import log_return
import pytest
import numpy as np
from pandas.testing import assert_frame_equal


# to test for asset_metrics() function
'''
1. Return type
    - Returns a pd.DataFrame
    - Not None, not a Series, not a dict
'''
def test_asset_metrics_dtypes(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [2, 4, 6, 8],
        "C": [3, 6, 9, 12]
    }

    df = pd.DataFrame(data)

    df_log_return = log_return(df, 'Date')

    result = asset_metrics(df_log_return, 'Date')

    assert isinstance(result, pd.DataFrame)

'''
2. Columns
    - All expected column names exist
    - Column names match exactly (including symbols like μ, σ)
    - Column order is correct
'''
def test_asset_metrics_col(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [2, 4, 6, 8],
        "C": [3, 6, 9, 12]
    }

    df = pd.DataFrame(data)

    df_log_return = log_return(df, 'Date')

    df_result = asset_metrics(df_log_return, 'Date')

    col_result = list(df_result.columns)

    col_expected = [
        "Annualised Return (μ)", 
        "StdDev (Volatility σ)", 
        "Cumulative Return", 
        "Observations"]

    assert col_result == col_expected



'''
3. Index
    - Index values match ticker_order
    - Index order is correct
    - Index name (if any) is as expected
    - Missing tickers produce NaN (if allowed)
    - Extra tickers are dropped (if expected)
4. Shape
    - Number of rows == len(ticker_order)
    - Number of columns == expected metric count
5. Values (content correctness)
    - Each column equals the corresponding input series
    - Values are aligned correctly after reindex
    - No unintended mixing between tickers
    - NaNs appear only where expected
6. Dtypes
    - Return/volatility columns are floats
    - Observation counts are ints (or nullable ints)
    - No accidental object dtype
7. Ordering guarantees
    - Reindexing actually changes order when ticker_order ≠ original index
    - Stable order when ticker_order matches original
8. Numerical correctness (if computed upstream)
    - Values are equal within tolerance (rtol, atol)
    - No silent rounding or truncation
9. Edge cases
    - Empty ticker_order
    - Single ticker
    - Missing metrics for a ticker
    - Extra metrics in input
    - All-NaN column
10. Immutability / side effects
    - Input series unchanged
    - Original index order preserved in inputs
11. Error handling (if applicable)
    - Meaningful error if inputs have mismatched indexes
    - Meaningful error if ticker_order contains unknown tickers
'''