# packages
from datetime import date
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_tags import st_tags
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border

# scripts
from stock_api import ticker_closed_price
from corr_matrix import corr_matrix
from heatmap import heatmap
from line_chart import line_chart
from create_xlsx import create_xlsx

# streamlit page config
st.set_page_config(
    page_title="Stock Correlation Calculator",
    layout="wide"
)

# Title
st.title("Stock Correlation Calculator")
st.markdown("This app uses the Yahoo Finance API to query the daily stock price of the selected stocks within the date range.  \nThe data is then used to return the price chart and calculate the correlation between each selected stock.  \nYou can add or remove stocks, and amend the date range using the input boxs below.  \nPlease refer to Yahoo Fiance for the correct ticker references. ")

# fields input
st.header("Select the stock and date range: ")

tickers = st_tags(
    label = "Tickers: ",
    text='Press enter to add more',
    value=["AAPL", "TSLA", "BARC.L", "VOO", "QQQ", "GLD", "GBPJPY=X"],
    suggestions=["NVDA", "GOOG", "MSFT"],
    maxtags = 20,
    key='1')

start, end, filler = st.columns([1, 1, 2])

with start:
    start_date = st.date_input(
        "Start Date: ",
        date.today().replace(year = date.today().year-1),
        max_value = date.today(),
        format = "YYYY-MM-DD")

with end:
    end_date = st.date_input(
        "End Date: ",
        date.today(),
        max_value = date.today(),
        format = "YYYY-MM-DD")
# start_date = "2023-01-01"
# end_date = date.today()
# st.text(date.today().year-1)
# st.text(date.today().replace(year = date.today().year-1))

# api call and data cleaning
closed_price_wide = ticker_closed_price(tickers, start_date, end_date)
closed_price_long = (
    pd.melt(closed_price_wide,
            id_vars = ["Date"],
            value_vars = tickers,
            var_name = "Ticker",
            value_name = "Closed_price")
    .sort_values(by="Date", ignore_index = True)
)


st.header("Closed Price")
st.caption(f"Time period: {start_date} to {end_date}")
st.altair_chart(line_chart(closed_price_long), use_container_width=True)

# Corelation matrix
matrix = corr_matrix(closed_price_wide)

# Colored table for matrix

heatmap = heatmap(matrix)

st.header("Correlation Matrix")
date_not_null = closed_price_wide.dropna()
min = date_not_null['Date'].min().strftime("%Y-%m-%d")
max = date_not_null['Date'].max().strftime("%Y-%m-%d")

st.caption(f"Date range for calculation: {min} to {max}  \n*The correlation between stocks are caluclated using dates where price of all stocks are available. Dates with missing price are not used in the calculation. ")

st.table(heatmap)

# Data Export

st.header("Download data as xlsx file")

if st.download_button(
        label = "Download",
        data = create_xlsx(closed_price_wide, matrix),
        file_name = "stock_data.xlsx"
        ):
    st.write("Thank you for downloading. ")


