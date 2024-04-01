from stock_api import ticker_closed_price
import pytest

def test_invalid_date():
    with pytest.raises(ValueError):
        assert ticker_closed_price(["AAPL", "TSLA"], "2024-01-01", "2023-01-01")

def test_ticker_error():
    with pytest.raises(ValueError):
        assert ticker_closed_price(["AAPL"], "2024-01-01", "2024-02-01")