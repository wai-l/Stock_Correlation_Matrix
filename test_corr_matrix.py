from corr_matrix import corr_matrix
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal


def test_matrix_positive():
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [1, 2, 3, 4],
        "C": [2, 4, 6, 8]
    }

    df = pd.DataFrame(data)

    expected = pd.DataFrame({
        "A": [1.0, 1.0, 1.0],
        "B": [1.0, 1.0, 1.0],
        "C": [1.0, 1.0, 1.0]
    }, index = ['A', 'B', 'C'])

    result = corr_matrix(df)

    assert_frame_equal(result, expected)


def test_matrix_negative():
    data = {
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        "A": [1, 2, 3, 4],
        "B": [4, 3, 2, 1],
        "C": [8, 6, 4, 2]
    }

    df = pd.DataFrame(data)

    expected = pd.DataFrame({
        "A": [1.0, -1.0, -1.0],
        "B": [-1.0, 1.0, 1.0],
        "C": [-1.0, 1.0, 1.0]
    }, index = ['A', 'B', 'C'])

    result = corr_matrix(df)

    assert_frame_equal(result, expected)


def test_matrix_2rows():
    with pytest.raises(ValueError):
        data = {
            "Date": ["2024-01-01", "2024-01-02"],
            "A": [1, 2],
            "B": [4, 3]
            }
        df = pd.DataFrame(data)
        result = corr_matrix(df)

def test_matrix_na():
    with pytest.raises(ValueError):
        data = {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "A": [1, pd.NA, 3, pd.NA],
            "B": [4, 3, 2, 1],
            "C": [8, 6, 4, 2]
            }
        df = pd.DataFrame(data)
        result = corr_matrix(df)

def test_matrix_all_na():
    with pytest.raises(ValueError):
        data = {
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
            "A": [pd.NA, pd.NA, pd.NA, pd.NA],
            "B": [pd.NA, pd.NA, pd.NA, pd.NA],
            }
        df = pd.DataFrame(data)
        result = corr_matrix(df)