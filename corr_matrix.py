import pandas as pd

# def main():
#     data = {
#         "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
#         "age": [2, 10, 3, 10],
#         "score": [10, 11, 13, None],
#         "fee": [None, None, None, None]
#         }

#     df = pd.DataFrame(data)
#     print(df)
#     print(corr_matrix(df))

def corr_matrix(df):
    nrow = len(df.dropna(axis=0))

    # dates with na are excluded in the calculatio
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

# if __name__ == "__main__":
#     main()