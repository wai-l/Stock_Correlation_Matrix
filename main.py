# packages
from datetime import date, datetime
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from streamlit_tags import st_tags
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border

# scripts
from app_lib.stock_api import ticker_closed_price
from app_lib.corr_matrix import corr_matrix
from app_lib.heatmap import heatmap
from app_lib.line_chart import line_chart
from app_lib.xlsx_summary_report import xlsx_summary_report
from app_lib.data_transform import log_return
from app_lib.metrics import asset_metrics, portfo_metrics

# streamlit page config
st.set_page_config(
    page_title="Portfolio Correlation Calculator V2",
    layout="wide"
)

# Title
st.title("Portfolio Correlation Calculator V2")
# this need rewritten
st.markdown("This app uses the Yahoo Finance API to query the daily price of the selected assets within the date range. The data is then used to return the price chart and calculate the correlation between each selected stock. You can add or remove stocks, and amend the date range using the input boxs below. Please refer to Yahoo Fiance for the correct ticker references. ")

input_fields, filler, portfo_summary = st.columns([9, 1, 9])

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

    df_pending = st.data_editor(df, 
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


    if st.button('Calculate', type='primary', ): 
        edited_df = df_pending.copy()
    else: 
        edited_df = df.copy()

    tickers = edited_df['Tickers'].to_list()

    total_allocated = edited_df['Allocation Percentage'].sum()

    errors = []

    if total_allocated > 100:
        errors.append(f"The total allocation percentage is {total_allocated:.2f}%. Please adjust the values so that they do not exceed 100%.")

    if edited_df.empty:
        errors.append("The portfolio is empty. Please add at least one asset.")

    if (edited_df["Allocation Percentage"] < 0).any():
        errors.append("Allocation percentages must be non-negative. Please correct the values.")

    if len(edited_df["Tickers"]) != len(set(edited_df["Tickers"])):
        errors.append("Duplicate tickers found in the portfolio. Please ensure all tickers are unique.")
    
    if edited_df["Tickers"].isnull().any() or edited_df["Tickers"].str.strip().eq("").any():
        errors.append("Ticker symbols cannot be empty. Please provide valid ticker symbols.")

    if errors:
        for msg in errors:
            st.error(msg)
        st.stop()


with portfo_summary: 
    # api call and data cleaning
    closed_price_wide = ticker_closed_price(tickers, start_date, end_date)
    log_return_df = log_return(closed_price_wide)
    portfo_m = portfo_metrics(log_return_df, edited_df)

    # portfoliio metrics
    st.header('Portfolio Summary')

    col1, col2= st.columns(2)
    col1.metric('Number of Assets', len(tickers))
    col2.metric('Total Allocation', f"{total_allocated:.2f}%")

    st.subheader('Annualised', help='Based on 252 trading days per year. ')
    
    col1, col2, col3 = st.columns(3)
    col1.metric(
        'Expected Return (μ)', 
        f"{portfo_m['Expected Return (μ)']:.2%}"
        )
    col2.metric(
        'StdDev (Volatility σ)', 
        f"{portfo_m['StdDev (Volatility σ)']:.2%}"
        )
    col3.metric(
        'Sharpe Ratio', 
        f"{portfo_m['Sharpe Ratio']:.2f}", 
        help='Assuming risk-free rate is 4.5%'
        )
    
    st.subheader('Cumulative')
    col1, col2, col3 = st.columns(3)
    col1.metric(
        'Max Drawdown', 
        f"{portfo_m['Max Drawdown']:.2%}")
    col2.metric(
        'Cumulative Return', 
        f"{portfo_m['Cumulative Return']:.2%}")



asset_metrics_display, filler, corr_matrix_display = st.columns([9, 1, 9])

with asset_metrics_display:  
    st.header('Assets Metrics')
    metrics_df = asset_metrics(log_return_df)
    st.dataframe(
        metrics_df.style.format({
            'Annualised Return (μ)': '{:.2%}',
            'StdDev (Volatility σ)': '{:.2%}',
            'Cumulative Return': '{:.2%}',
            'Observations': '{:,.0f}'
        }),
        column_config={
            'Observations': st.column_config.NumberColumn(
                'Observations',
                help='Number of valid log-return observations for the asset'
            )
        }
    )

with corr_matrix_display:
    # Corelation matrix
    daily_return = log_return(closed_price_wide)
    matrix = corr_matrix(daily_return)

    # Colored table for matrix

    heatmap = heatmap(matrix)

    st.header(
        "Correlation Matrix", 
        help="The correlation between stocks are caluclated using dates where price of all stocks are available. Dates with missing price are not used in the calculation. ")
    date_not_null = closed_price_wide.dropna()
    min = date_not_null['Date'].min().strftime("%Y-%m-%d")
    max = date_not_null['Date'].max().strftime("%Y-%m-%d")

    st.table(heatmap)

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


# Data Export

st.header("Download data as xlsx file")

now = datetime.now()
now = now.strftime("%Y%m%d_%H%M%S")

if st.download_button(
        label = "Download",
        data = xlsx_summary_report(closed_price_wide, matrix),
        file_name = f'{now}_porfo_cor_cal_summary.xlsx'
        ):
    st.write("Thank you for downloading. ")


