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
from app_lib.xlsx_summary_report import xlsx_summary_report, build_portfolio_export
from app_lib.data_transform import log_return, normalize_to_100
from app_lib.metrics import asset_metrics, portfo_metrics
from app_lib.streamlit_helper import highlight_total_row

# streamlit page config
st.set_page_config(
    page_title="Portfolio Correlation Calculator V2",
    layout="wide"
)

default_portfolio = pd.DataFrame({
    "Tickers": ["AAPL", "TSLA", "BARC.L", "VOO", "QQQ", "GLD", "USDGBP=X"],
    "Allocation Percentage": [15, 15, 10, 20, 20, 10, 10],
})

st.session_state.setdefault("applied_df", default_portfolio)
st.session_state.setdefault("applied_start", date.today().replace(year=date.today().year - 1))
st.session_state.setdefault("applied_end", date.today())
st.session_state.setdefault("price_display_mode", "Price")


# Title
st.title("Portfolio Correlation Calculator V2")
# this need rewritten
st.markdown("This app uses the Yahoo Finance API to query the daily price of the selected assets within the date range. The data is then used to calculate performance metrics and correlation between each selected stock. You can add or remove stocks, and amend the date range using the input boxs below. Please refer to Yahoo Fiance for the correct ticker references. ")

input_fields, filler, portfo_summary = st.columns([9, 1, 9])



with input_fields:
    st.header("Select the date range and the assets:")

    with st.form("inputs_form", clear_on_submit=False):
        start, end, _filler = st.columns([1, 1, 2])


        with start: 
            start_date = st.date_input(
                "Start Date",
                value=st.session_state["applied_start"],
                max_value=date.today(),
                format="YYYY-MM-DD",
            )

        with end: 
            end_date = st.date_input(
                "End Date",
                value=st.session_state["applied_end"],
                max_value=date.today(),
                format="YYYY-MM-DD",
            )
        
        st.text("Portfolio Allocation (%)")
        df_pending = st.data_editor(
            st.session_state["applied_df"].reset_index(drop=True), 
            num_rows="dynamic",
            width="stretch",
            hide_index=True, 
            column_config={
                "Tickers": st.column_config.TextColumn("Tickers"),
                "Allocation Percentage": st.column_config.NumberColumn(
                    "Allocation Percentage",
                    min_value=0,
                    max_value=100,
                    step=0.01,
                    format="%.2f%%",
                ),
            },
        )
        
        submitted = st.form_submit_button("Calculate", type="primary")

    if submitted:
        # apply inputs once
        st.session_state["applied_start"] = start_date
        st.session_state["applied_end"] = end_date

        applied = df_pending.dropna(how="all").reset_index(drop=True).copy()
        applied["Tickers"] = applied["Tickers"].astype(str).str.strip()
        applied["Allocation Percentage"] = pd.to_numeric(applied["Allocation Percentage"], errors="coerce")

        st.session_state["applied_df"] = applied
        st.rerun()

    edited_df = st.session_state["applied_df"]
    tickers = edited_df["Tickers"].tolist()

    start_date = st.session_state["applied_start"]
    end_date = st.session_state["applied_end"]

    # put start_date and end_date into para dataframe for export
    para_df = pd.DataFrame(
        {'Parameter': ['start_date', 'end_date'], 
         'Value': [start_date, end_date]}
    )
    

    total_allocated = edited_df["Allocation Percentage"].sum()

    errors = []

    if total_allocated > 100:
        errors.append(f"The total allocation percentage is {total_allocated:.2f}%. Please adjust the values so that they do not exceed 100%.")

    if edited_df.empty:
        errors.append("The portfolio is empty. Please add at least one asset.")

    if (edited_df["Allocation Percentage"] < 0).any():
        errors.append("Allocation percentages must be non-negative. Please correct the values.")

    if len(edited_df["Tickers"]) != len(set(edited_df["Tickers"])):
        errors.append("Duplicate tickers found in the portfolio. Please ensure all tickers are unique.")

    if edited_df["Tickers"].isnull().any() or edited_df["Tickers"].astype(str).str.strip().eq("").any():
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
    col3.metric(
        'Cumulative Return (Log)', 
        f"{portfo_m['Cumulative Return (Log)']:.2%}")

        # "Contribution (log)": cumulative_contrib_log,
        # "Contribution": simple_contrib,
        # "Contribution Share": contrib_share, 

        # # for error check
        # "Cumulative Return (Log)": cum_return_log, 
        # "Cumulative Contribution (Log) Sum": cum_contrib_log_sum, 
        # "Diff": cum_return_log - cum_contrib_log_sum
    
    # write a dataframe to store portfolio summary
    metric_gp_1 = pd.DataFrame(
        {
        'Metric': ['Number of Assets', 'Total Allocation'], 
        'Value': [len(tickers), total_allocated]
        }
    )

    metric_gp_2 = (
        pd.Series(
            {k: v for k, v in portfo_m.items() if np.isscalar(v)},
            name="Value",
        )
        .rename_axis("Metric")
        .reset_index()
    )
    
    metric_ignore = ['Cumulative Contribution (Log) Sum', 'Diff']

    metric_gp_2 = metric_gp_2[~metric_gp_2['Metric'].isin(metric_ignore)]

    port_metric = pd.concat([metric_gp_1, metric_gp_2])

asset_metrics_display, filler, asset_contrib = st.columns([9, 1, 9])

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

with asset_contrib: 
    # asset contribution display
    contri_1 = pd.DataFrame(portfo_m['Contribution (log)']).reset_index()
    contri_1.columns = ['Ticker', 'Contribution (log)']

    contri_2 = pd.DataFrame(portfo_m['Contribution Share']).reset_index()
    contri_2.columns = ['Ticker', 'Contribution Share']

    contri_df = (
        contri_1
        .merge(contri_2, on='Ticker')
    )

    totals = pd.DataFrame(
        {
            "Ticker": ["Total"],
            "Contribution (log)": [contri_df["Contribution (log)"].sum()],
            "Contribution Share": [contri_df["Contribution Share"].sum()]
        }
    )

    contri_df_with_total = pd.concat([contri_df, totals]).set_index('Ticker')


    st.header('Assets Contribution to Portfolio')
    st.dataframe(
        contri_df_with_total
        .style.apply(highlight_total_row, axis=1)
        .format(
            {
                'Contribution (log)': '{:.2%}',
                'Contribution': '{:.2%}',
                'Contribution Share': '{:.2%}'
            }
        ),
        width='stretch'
    )


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

# Closed Price display (chart and table)
## select for price/percentage change
st.header("Closed Price by Assets and Date")
st.caption(f"Time period: {start_date} to {end_date}")

price_display_options = ['Price', 'Indexed']
price_display_selection = st.segmented_control(
    "Value", price_display_options, 
    key='price_display_mode'
)

normalised_price_df = normalize_to_100(
    df=closed_price_wide, 
    date_col='Date', 
    base=100.0
)

display_data = (
    normalised_price_df
    if st.session_state["price_display_mode"] == "Indexed"
    else closed_price_wide
)

# Closed Price Line Chart
display_long = (
    pd.melt(display_data,
            id_vars = ["Date"],
            value_vars = tickers,
            var_name = "Ticker",
            value_name = "Closed_price")
    .sort_values(by="Date", ignore_index = True)
)


st.caption(f'Index option base = 100 at first available price date for each asset.')

st.subheader("Closed Price Chart")

st.altair_chart(line_chart(display_long), width='stretch')

st.subheader("Closed Price Data")
# Closed Price Data Table
## display closed price data
### price as 2 decimal places
### date as YYYY-MM-DD

display_data["Date"] = display_data["Date"].dt.strftime("%Y-%m-%d")

st.dataframe(
    display_data.style.format(
        {col: '{:.2f}' for col in display_data.columns if col != 'Date'}
    ),
    width='stretch'
)

# Data Export

st.header("Download data as xlsx file")

now = datetime.now()
now = now.strftime("%Y%m%d_%H%M%S")

xlsx_buf = build_portfolio_export(
    para=para_df, 
    portfolio_allocation=edited_df, 
    portfo_summary=port_metric, 
    asset_metric=metrics_df, 
    asset_contrib=contri_df, 
    price_history=closed_price_wide, 
    price_history_indexed=normalised_price_df, 
    corr_matrix=matrix
    )

if st.download_button(
        label = "Download",
        data = xlsx_buf.getvalue(),
        file_name = f'{now}_porfo_cor_cal_summary.xlsx'
        ):
    st.write("Thank you for downloading. ")


