# packages
from datetime import date
import pandas as pd
import numpy as np
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
from data_transform import log_return

# streamlit page config
st.set_page_config(
    page_title="Portfolio Correlation Calculator V2",
    layout="wide"
)

# Title
st.title("Portfolio Correlation Calculator V2")
# this need rewritten
st.markdown("This app uses the Yahoo Finance API to query the daily price of the selected assets within the date range. The data is then used to return the price chart and calculate the correlation between each selected stock. You can add or remove stocks, and amend the date range using the input boxs below. Please refer to Yahoo Fiance for the correct ticker references. ")

input_fields, portfo_summary = st.columns(2)

with input_fields: 
# fields input
    st.header("Select the date range and the assets: ")

    start, end, filler = st.columns([1, 1, 2])

    with start: 
        st.text('Start Date: ')
        start_date = st.date_input(
            "Start Date: ",
            date.today().replace(year = date.today().year-1),
            max_value = date.today(),
            format = "YYYY-MM-DD", 
            label_visibility='collapsed')

    with end: 
        st.text('End Date: ')
        end_date = st.date_input(
            "End Date: ",
            date.today(),
            max_value = date.today(),
            format = "YYYY-MM-DD", 
            label_visibility='collapsed')

    st.text('Portfolio allocation: ')

    df = pd.DataFrame(
        {
            "Tickers": ['AAPL', 'TSLA', 'BARC.L', 'VOO', 'QQQ', 'GLD', 'USDGBP=X'],
            "Allocation Percentage": [15, 15, 10, 20, 20, 10, 10]
        }
    )

    edited_df = st.data_editor(df, 
                            num_rows="dynamic", 
                            use_container_width=True, 
                            column_config={
                                "Tickers": st.column_config.TextColumn(
                                    "Tickers",
                                    help="Enter the stock ticker symbol"
                                ),
                                "Allocation Percentage": st.column_config.NumberColumn(
                                    "Allocation Percentage",
                                    help="Enter the allocation percentage for each stock (up to 2 decimals)",
                                    min_value=0,
                                    max_value=100,
                                    step=0.01, 
                                    format='%.2f%%'
                                )
                            },
                            )

    tickers = edited_df['Tickers'].to_list()

    total_allocated = edited_df['Allocation Percentage'].sum()

    if total_allocated > 100: 
        st.error("The total allocation percentage exceeds 100%. Please adjust the values.")
        st.stop()

with portfo_summary: 
    # api call and data cleaning
    closed_price_wide = ticker_closed_price(tickers, start_date, end_date)

    # portfoliio metrics
    st.header('Portfolio Summary')

    col1, col2= st.columns(2)
    col1.metric('Number of Assets', len(tickers), help='testing', )
    col2.metric('Total Allocation', f"{total_allocated:.2f} %")

    col1, col2 = st.columns(2)
    col1.metric('Expected Returns (Annualised)', f'{np.random.uniform(5, 15):.2f} %')
    col2.metric('StdDev (Volatility σ)', f'{np.random.uniform(10, 30):.2f} %')

    col1, col2 = st.columns(2)
    col1.metric('Sharpe Ratio', f'{np.random.uniform(0.5, 2):.2f} ')
    col2.metric('Max Drawdown', f'{np.random.uniform(5, 15):.2f} %')

chart, corr_matrix_display = st.columns(2)

with chart: 
    # Closed Price Line Chart
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

with corr_matrix_display:
    # Corelation matrix
    daily_return = log_return(closed_price_wide)
    matrix = corr_matrix(daily_return)

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


