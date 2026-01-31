import pandas as pd
import pytest
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.data_transform import log_return
import pytest
import numpy as np
from pandas.testing import assert_frame_equal
from numpy.testing import assert_allclose
import warnings


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

'''
1. Return type
    - Returns a dictionary
'''
def test_portfo_metrics_dtypes(): 
    portfo_return = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [2, 4, 6, 8],
        "C": [3, 6, 9, 12]
    }

    portfo_return_df = pd.DataFrame(portfo_return)

    log_return_df = log_return(portfo_return_df, 'Date')

    allocation_df = pd.DataFrame({
        "Tickers": ["A", "B", "C"],
        "Allocation Percentage": [80, 10, 10],
    })

    result = portfo_metrics(log_return_df, allocation_df)

    assert isinstance(result, dict)


'''
2.1. Values - Expected Return
'''
def test_profo_metrics_expected_return(): 

    days = 252

    # log_return
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

    result = portfo_metrics(portfo_return_df, allocation_df, trading_days=days)['Expected Return (μ)']

    # expected: 
    a_expected = np.mean(portfo_return['A'])*days
    b_expected = np.mean(portfo_return['B'])*days
    c_expected = np.mean(portfo_return['C'])*days
    d_expected = np.mean(portfo_return['D'])*days

    expected = a_expected*0.7 + b_expected*0.05 + c_expected * 0.1 + d_expected * 0.15

    assert_allclose(
        actual = result, 
        desired = expected, 
        equal_nan = True
    )

'''
2.2. Values - value error
'''

def test_profo_metrics_value_error(): 

    with pytest.raises(ValueError): 

        days = 252

        # actual price
        portfo_return = {
            "Date": ["2024-01-01"],
            "A": [1],
            "B": [2]
        }

        portfo_return_df = pd.DataFrame(portfo_return)

        log_return_df = log_return(portfo_return_df)

        allocation_df = pd.DataFrame({
            "Tickers": ["A", "B"],
            "Allocation Percentage": [70, 30],
        })

        result = portfo_metrics(log_return_df, allocation_df, trading_days=days)


    with pytest.raises(ValueError): 
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

        result = portfo_metrics(log_return_df, allocation_df, trading_days=days)

        print(result)

'''
2.3. Values - Standard Deviation
'''

def test_profo_metrics_std_dev(): 

    days = 252

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

    result = portfo_metrics(portfo_return_df, allocation_df, trading_days=days)['StdDev (Volatility σ)']

    # expected
    # allocation_df['Allocation Percentage'] = allocation_df['Allocation Percentage']/allocation_df['Allocation Percentage'].sum()

    portfo_retrun_weighted = {
    'Date': portfo_return_df['Date'], 
    'A': portfo_return_df['A']*0.7,
    'B': portfo_return_df['B']*0.05,
    'C': portfo_return_df['C']*0.1,
    'D': portfo_return_df['D']*0.15
}

    portfo_return_weighted_df = pd.DataFrame(portfo_retrun_weighted)

    portfo_return_weighted_df['Portfolio'] = (
        portfo_return_weighted_df
        .drop(columns=['Date'])
        .sum(axis=1)
    )

    weighted_return = portfo_return_weighted_df['Portfolio']

    portfo_return_mean = portfo_return_weighted_df['Portfolio'].mean()

    # 0: 0.75; 1: 0.9; 2: 1.05; 3: 1.2
    # mean = 0.974999999999

    expected = (
        np.sqrt(
            np.sum([
                np.square(weighted_return[0]-portfo_return_mean), 
                np.square(weighted_return[1]-portfo_return_mean), 
                np.square(weighted_return[2]-portfo_return_mean), 
                np.square(weighted_return[3]-portfo_return_mean)
                ]
                )/3
            ) * np.sqrt(252)
        )
    
    assert_allclose(
        actual = result, 
        desired = expected, 
        equal_nan = True
    )

        
'''
2.4. Values - Sharpe Ratio
'''

def test_profo_metrics_sharpe_ratio(): 

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

    ## other factors for expected sharpe ratio

    expected_std = portfo_metrics(
        portfo_return_df, 
        allocation_df, 
        trading_days=days
        )['StdDev (Volatility σ)']

    # we don't have to do return - rf here because it's already in mu_excess
    expected = mu_excess / expected_std

    assert_allclose(
        actual = result, 
        desired = expected, 
        equal_nan = True, 

    )

'''
2.5. Values - Max Drawdown
'''

def test_profo_metrics_max_drawdown():
    '''
    max drawdown (%) = max(peak - trough) / peak
    '''
    pass
    # below is from co pilot and need review
    days = 252

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

    result = portfo_metrics(
        portfo_return_df, 
        allocation_df, 
        trading_days=days
        )['Max Drawdown']

    # expected
    portfo_retrun_weighted = {
        'Date': portfo_return_df['Date'], 
        'A': portfo_return_df['A']*0.7,
        'B': portfo_return_df['B']*0.05,
        'C': portfo_return_df['C']*0.1,
        'D': portfo_return_df['D']*0.15
    }

    portfo_return_weighted_df = pd.DataFrame(portfo_retrun_weighted)

    portfo_return_weighted_df['Portfolio'] = (
        portfo_return_weighted_df
        .drop(columns=['Date'])
        .sum(axis=1)
    )

    weighted_return = portfo_return_weighted_df['Portfolio']

    cumulative = (1 + weighted_return).cumprod()

    peak = cumulative.cummax()

    drawdown = (peak - cumulative) / peak

    expected = drawdown.max()

    assert_allclose(
        actual = result, 
        desired = expected, 
        equal_nan = True
    )

