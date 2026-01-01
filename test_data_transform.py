from app_lib.data_transform import log_return, normalize_to_100
import pandas as pd
import numpy as np
import pytest
from pandas.testing import assert_frame_equal

def test_log_return_standard(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [2, 4, 6, 8],
        "C": [3, 6, 9, 12]
    }

    df = pd.DataFrame(data)

    result = log_return(df, 'Date')

    expected = df.copy()

    cols = ['A', 'B', 'C']

    for i in cols: 
        expected[i] = np.log(expected[i])
        expected[i] = expected[i].diff()

    assert_frame_equal(result, expected)

def test_log_return_partial_nan(): # test case when there's nan in the middle rows
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, np.nan, 2, 3],
        "B": [2, 4, np.nan, 6],
        "C": [3, 6, 9, np.nan]
    }
    
    df = pd.DataFrame(data)

    df_exp = df.copy()

    cols = ['A', 'B', 'C']

    for i in cols: 
        df_exp[i] = np.exp(df_exp[i])

    result = log_return(df_exp, 'Date')

    expected_data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [np.nan, np.nan, 1, 1],
        "B": [np.nan, 2, np.nan, 2],
        "C": [np.nan, 3, 3, np.nan]
    }

    expected = pd.DataFrame(expected_data)

    assert_frame_equal(result, expected)

def test_normalize_to_100_standard(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [200, 300, 400, 500],
        "C": [4, 3, 2, 1], 
        "D": [100, 90, 80, 70], 
        "E": [200, 100, 300, 500]
    }

    df = pd.DataFrame(data)

    result = normalize_to_100(df=df, date_col = 'Date')

    expected_data = {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "A": [100, 200, 300, 400],
            "B": [100, 150, 200, 250],
            "C": [100, 75, 50, 25], 
            "D": [100, 90, 80, 70], 
            "E": [100, 50, 150, 250]
        }

    expected = pd.DataFrame(expected_data)

    cols = ['A', 'B', 'C', 'D', 'E']

    for col in cols: 
        expected[col] = expected[col].astype(float)

    assert_frame_equal(result, expected)

def test_normalize_to_100_null(): 
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [np.nan, 1, 2, 3],
        "B": [200, np.nan, 400, 500],
        "C": [4, 3, np.nan, 1], 
        "D": [100, 90, 80, np.nan]
    }

    df = pd.DataFrame(data)

    result = normalize_to_100(df=df, date_col = 'Date')

    expected_data = {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "A": [np.nan, 100, 200, 300],
            "B": [100, np.nan, 200, 250],
            "C": [100, 75, np.nan, 25], 
            "D": [100, 90, 80, np.nan]
        }

    expected = pd.DataFrame(expected_data)

    cols = ['A', 'B', 'C', 'D']

    for col in cols: 
        expected[col] = expected[col].astype(float)

    assert_frame_equal(result, expected)