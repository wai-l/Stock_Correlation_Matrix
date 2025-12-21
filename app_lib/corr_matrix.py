import pandas as pd
import numpy as np

def main():
    # data = {
    #     "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    #     "age": [2, 10, 3, 10],
    #     "score": [10, 11, 13, None]
    #     }
    # df = pd.DataFrame(data)

    # read data
    price = pd.read_csv('./testing/testing_stock_data_2.csv')

    # print(price['AAPL'].head())
    # print(price['AAPL'].shift(1).head())

    # calculate price change
    ## return = ln(price(n)/price(n-1))
    price.iloc[:, 1:] = price.iloc[:, 1:].apply(lambda x: np.log(x) - np.log(x.shift(1)))

    # assign dataframe for correlation calculation
    df = price

    # print(df.head())
    print(corr_matrix(df))

    # cols_to_review = ['VOO', 'AAPL', 'NVDA']
    # for col in cols_to_review:
    #     col_mean = df[col].mean()
    #     col_sum = df[col].sum()
        
    #     print(f"{col} mean: {col_mean}, sum: {col_sum}")
        



def corr_matrix(df):
    nrow = len(df.dropna(axis=0))

    # dates with na are excluded in the calculation by default in the corr() function
    if nrow >= 3:
        matrix = (
            df
            .drop('Date', axis = 1)
            .corr(min_periods = 3)
        )
        return matrix
    else:
        raise ValueError("There are less then 3 rows with valid price data")

#     # Corelation matrix
# # dates with na are excluded in the calculation
# matrix = (
#     closed_price_wide
#     .drop('Date', axis = 1)
#     .corr(min_periods = 3)
# )

# # print an error msg for when non-na rows are 2 or less
# # error promt for zero / blank

if __name__ == "__main__":
    main()