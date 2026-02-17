from app_lib.stock_api import ticker_closed_price, PriceDownloadError
import pytest

def test_invalid_date():
    with pytest.raises(ValueError):
        assert ticker_closed_price(["AAPL", "TSLA"], "2024-01-01", "2023-01-01")

def test_not_enough_valid_tickers():
    # Only 1 ticker -> should fail because min_valid=2
    with pytest.raises(PriceDownloadError):
        ticker_closed_price(["AAPL"], "2024-01-01", "2024-02-01")
