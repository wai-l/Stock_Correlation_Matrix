import pandas as pd
import altair as alt

def line_chart(df):
    # remove na for plotting
    df = df.dropna()

    # Creat a list of the tickers sorted by their latest price
    # The sorted list was grouped by Tickers, with na removed
    # Therefore when some tickers have missing data on the latest date,
    # The latest data for that particular ticker will be used in sorting
    # This is used so the the legend order will follow the end point of the lines
    sorted_list = (
        df
        .groupby('Ticker')
        .apply(lambda x: x[x['Date'] == x['Date'].max()])
        .sort_values('Closed_price', ascending=False)
        ['Ticker']
        .tolist()
        )

    hover = alt.selection_point(
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty=False,
    )

    lines = (
        alt.Chart(df)
        .mark_line(interpolate='linear')
        .encode(
            alt.X('Date:T').axis(format='%Y-%m-%d').title('Date'),
            alt.Y('Closed_price:Q').title('Price (Closed)'),
            color=alt.Color('Ticker:N',
                        sort=sorted_list).title("Tickers"),
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(df)
        .mark_rule()
        .encode(
            x="Date",
            y="Closed_price",
            opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
            tooltip=[
                alt.Tooltip('Date:T', title = 'Date', format = '%Y-%m-%d'),
                alt.Tooltip('Ticker', title = 'Ticker'),
                alt.Tooltip('Closed_price', title='Closed Price', format='.2f')
            ],
            stroke=alt.value('#D4D4D4')
        )
        .add_params(hover)
    )
    return (lines + points + tooltips).interactive()
