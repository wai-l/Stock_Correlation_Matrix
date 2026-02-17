from app_lib.heatmap import heatmap
import pandas as pd

def test_heatmap():
    df = pd.DataFrame({"A": [-1, 0, 1],
                       "B": [1, 0, -1]})
    styled_df = heatmap(df)
    assert isinstance(styled_df, pd.io.formats.style.Styler)

def test_heatmap_na():
    df = pd.DataFrame({"A": [0, 1, None],
                       "B": [1, None, -1]})
    styled_df = heatmap(df)
    assert isinstance(styled_df, pd.io.formats.style.Styler)