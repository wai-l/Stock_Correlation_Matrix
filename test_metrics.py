import pandas as pd
import pytest
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.data_transform import log_return
import pytest
import numpy as np
from pandas.testing import assert_frame_equal
from numpy.testing import assert_allclose


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
'''
def test_asset_metrics_index(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "C": [2, 4, 6, 8],
        "B": [3, 6, 9, 12]
    }

    df = pd.DataFrame(data)

    df_result = asset_metrics(df, 'Date')

    result = df_result.index.tolist()

    expected = ['A', 'C', 'B']

    assert result == expected

'''
4. Shape
    - Number of rows == len(ticker_order)
    - Number of columns == expected metric count
'''
def test_asset_metrics_shape(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "C": [2, 4, 6, 8],
        "B": [3, 6, 9, 12]
    }

    df = pd.DataFrame(data)

    df_result = asset_metrics(df, 'Date')

    result = df_result.shape

    expected = (3, 4)

    assert result == expected

'''
5. Values (content correctness)
    - Each column equals the corresponding input series
    - Values are aligned correctly after reindex
    - No unintended mixing between tickers
    - NaNs appear only where expected
'''
def test_asset_metrics_cal_basics(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [0, 0, 0, 0],
        "B": [np.nan, np.nan, np.nan, np.nan], 
        "C": [1, 1, 1, 1], 
        "D": [1, 1, np.nan, 1]
    }

    df = pd.DataFrame(data)

    result = asset_metrics(df, 'Date')

    data_expected = {
        'tickers': ['A', 'B', 'C', 'D'], 
        'Annualised Return (μ)': [0.00, np.nan, 252, 252], 
        'StdDev (Volatility σ)': [0.00, np.nan, 0.00, 0.00], 
        'Cumulative Return': [0.00, np.nan, np.exp(4)-1, np.exp(3)-1], 
        'Observations': [4.00, np.nan, 4.00, 3.00]
    }

    expected = (
        pd.DataFrame(data_expected)
        .set_index('tickers', drop=True)
        .rename_axis(None))

    assert_frame_equal(result, expected)

def test_asset_metrics_cal_annual_return(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [-1, 1, 1, -1], 
        "C": [1, 0, 0, 1], 
        "D": [1, 1, np.nan, 2]
    }

    df = pd.DataFrame(data)

    result_df = asset_metrics(df, 'Date').reset_index(drop=True)

    result = result_df['Annualised Return (μ)']

    a_expected = 10/4 * 252

    b_expected = 0

    c_expected = 0.5 * 252

    d_expected = 4/3 * 252

    expected = pd.Series([a_expected, b_expected, c_expected, d_expected])

    assert_allclose(
        actual = result.values, 
        desired = expected.values, 
        equal_nan = True
    )

def test_asset_metrics_cal_std(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [-1, 1, 1, -1], 
        "C": [2, 0, 0, 2], 
        "D": [1, 3, np.nan, 2]
    }

    df = pd.DataFrame(data)

    result_df = asset_metrics(df, 'Date').reset_index(drop=True)

    result = result_df['StdDev (Volatility σ)']

    a_expected = (
        np.sqrt(
            np.sum([
                np.square(1-2.5), 
                np.square(2-2.5), 
                np.square(3-2.5), 
                np.square(4-2.5)]
                )/3
            ) * np.sqrt(252))

    b_expected = np.sqrt(4/3) * np.sqrt(252)

    c_expected = b_expected

    d_expected = (
        np.sqrt(
            np.sum([
                np.square(1-2), 
                np.square(3-2), 
                np.square(2-2)]
                )/2
            ) * np.sqrt(252))

    expected = pd.Series([a_expected, b_expected, c_expected, d_expected])

    assert_allclose(
        actual = result.values, 
        desired = expected.values, 
        equal_nan = True
    )

def test_asset_metrics_cal_cum_return(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [-1, 1, 1, -1], 
        "C": [2, 0, 0, 2], 
        "D": [1, 3, np.nan, 2]
    }

    df = pd.DataFrame(data)

    result_df = asset_metrics(df, 'Date').reset_index(drop=True)

    result = result_df['Cumulative Return']

    a_expected = np.exp(10)-1

    b_expected = np.exp(0)-1

    c_expected = np.exp(4)-1

    d_expected = np.exp(6)-1

    expected = pd.Series([a_expected, b_expected, c_expected, d_expected])

    assert_allclose(
        actual = result.values, 
        desired = expected.values, 
        equal_nan = True
    )


def test_asset_metrics_cal_obs(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [1, 2, np.nan, 3], 
        "C": [2, 0, np.nan, np.nan], 
        "D": [np.nan, 1, np.nan, np.nan], 
        "E": [np.nan, np.nan, np.nan, np.nan]
    }

    df = pd.DataFrame(data)

    result_df = asset_metrics(df, 'Date').reset_index(drop=True)

    result = result_df['Observations']

    expected = pd.Series([4, 3, 2, 1, np.nan])

    assert_allclose(
        actual = result.values, 
        desired = expected.values, 
        equal_nan = True
    )

# repeat same strucutre for portfo_metrics