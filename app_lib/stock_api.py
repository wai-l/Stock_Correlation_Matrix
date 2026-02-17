import time
import pandas as pd
import yfinance as yf


class PriceDownloadError(RuntimeError):
    """Raised when we cannot obtain enough valid price series to proceed."""
    pass


def ticker_closed_price(
    tickers,
    start_date,
    end_date,
    min_valid: int = 2,
    max_retries: int = 3,
    retry_sleep_seconds: float = 2.0,
):
    """
    Download close prices for a list of tickers (wide format).

    Returns
    -------
    df_comb : pd.DataFrame
        Wide DataFrame with columns: Date + one column per *valid* ticker.
        (Only tickers with at least 1 non-null Close value are kept.)
    report : dict
        {
          "requested": [...],
          "valid": [...],
          "failed": { "TICKER": "reason", ... }
        }

    Notes
    -----
    - Skips individual tickers that fail or return all-null Close.
    - Retries the whole download call on transient errors (e.g. rate limit).
    """

    # ---- validate dates
    if start_date >= end_date:
        raise ValueError("Start date must be before end date.")

    # ---- normalize tickers
    if tickers is None:
        tickers = []
    tickers_norm = [str(t).strip().upper() for t in tickers if str(t).strip()]

    if len(tickers_norm) == 0:
        raise ValueError("Please input at least one ticker.")

    # De-duplicate while keeping order
    seen = set()
    tickers_norm = [t for t in tickers_norm if not (t in seen or seen.add(t))]

    last_err = None
    df = None

    # ---- download (retry on transient failures)
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                tickers=tickers_norm,
                start=start_date,
                end=end_date,
                group_by="ticker",
                auto_adjust=False,
                progress=False,
                threads=True,
            )
            last_err = None
            break
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(retry_sleep_seconds * attempt)  # simple backoff
            else:
                # We'll handle below
                pass

    if df is None or last_err is not None:
        raise PriceDownloadError(
            f"Price download failed after {max_retries} retries. "
            f"Details: {last_err}"
        )

    # ---- build wide close-price table
    close_series = {}
    failed = {}

    # yfinance returns different shapes depending on number of tickers.
    # For multi-ticker: df[ticker]["Close"] works (columns are MultiIndex).
    # For single ticker: df["Close"] is a Series/column.
    is_multi = isinstance(df.columns, pd.MultiIndex)

    for t in tickers_norm:
        try:
            if is_multi:
                # MultiIndex columns: (ticker, OHLCV)
                s = df[t]["Close"].rename(t)
            else:
                # Single ticker shape
                s = df["Close"].rename(t)

            # Validate the series has any usable data
            if s.isna().all():
                failed[t] = "No close price data returned (possible rate-limit, invalid ticker, or delisted)."
                continue

            close_series[t] = s

        except Exception as e:
            failed[t] = f"Failed to extract close prices: {e}"

    if len(close_series) == 0:
        raise PriceDownloadError(
            "No valid price series were returned. "
            "Try fewer tickers, shorten the date range, or wait and retry (rate limiting)."
        )

    df_comb = pd.concat(close_series.values(), axis=1).reset_index()

    # Ensure the date column is named consistently
    # yfinance uses 'Date' for regular prices, but sometimes it's 'index'
    if "Date" not in df_comb.columns:
        df_comb = df_comb.rename(columns={df_comb.columns[0]: "Date"})

    valid = list(close_series.keys())

    # ---- enforce minimum valid tickers for correlation/portfolio calcs
    if len(valid) < min_valid:
        raise PriceDownloadError(
            f"Only {len(valid)} ticker(s) returned valid data ({', '.join(valid)}). "
            f"Need at least {min_valid} to continue."
        )

    report = {
        "requested": tickers_norm,
        "valid": valid,
        "failed": failed,
    }

    return df_comb, report
