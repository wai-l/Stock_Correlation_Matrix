import yfinance as yf
import pandas as pd
import streamlit as st

# def main():
#     tickers = ["AAPL", "MSFT", "NVDA"]
#     start_date = "2024-01-01"
#     end_date = "2025-01-01"

#     print(ticker_closed_price(tickers, start_date, end_date))




def ticker_closed_price(tickers, start_date, end_date):

    # throw an exception handling for steamlit:
    # ['SPXP']: Exception('%ticker%: No timezone found, symbol may be delisted')
    # when end_date < start date
    # when ticker is unfound
    if start_date >= end_date:
        raise ValueError("Start date must be before end date. ")

    if len(tickers) < 2:
        raise ValueError("Please input two or more tickers. ")

    try:
        for i in range(len(tickers)):
            tickers[i] = tickers[i].upper()

        df = yf.download(tickers, start = start_date, end = end_date, group_by = "ticker")
        close_price_log = {}
        for ticker in tickers:
            close_price_log[ticker] = df[ticker]["Close"].rename(ticker)

        df_comb = pd.concat(close_price_log, axis = 1).reset_index()

        for ticker in tickers:
            if df_comb[ticker].isnull().all():
                raise ValueError(f"Cannot find any price data for '{ticker}', please check if the stock has been delisted. ")

        return(df_comb)

    except ValueError as ve:
        raise ValueError(f"A value error has occured: {ve}")

    except Exception as e:
        raise ValueError(f"An unexpected error has occured: {e}")


# main()