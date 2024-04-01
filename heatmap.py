import pandas as pd

def heatmap(df):
    heatmap = (
        df.style
        .format(precision = 4)
        .set_table_attributes('style="border-collapse:collapse"')
        .background_gradient(axis=None, vmin=-1, vmax=1, cmap="RdYlGn")
        .set_table_styles([{
            'selector': 'td, th',
            'props':
            [('font-family', 'Calibri, sans-serif'),
            ('min-width', '75px'),
            # ('text-align', 'center')
            ]
            }])
        )

    return heatmap