import pandas as pd
import io
from openpyxl.styles import Font, Alignment, Border

def create_xlsx(df1, df2):
    # the buffer is to let the excel file be the returning value of the function
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='price_history', index=False, header=True)
        df2.to_excel(writer, sheet_name='correlation_matrix', index=True, header=True)
        worksheet1 = writer.sheets['price_history']
        worksheet2 = writer.sheets['correlation_matrix']

    # Apply formatting to first row and first column
        for worksheet in [worksheet1, worksheet2]:
            # first row
            for cell in worksheet['1:1']:
                cell.font = Font(bold=False)
                cell.alignment = Alignment(horizontal='left', vertical='center')
                cell.border = None
            # first column
            for row in worksheet.iter_rows(min_row=2, min_col=1):
                for cell in row:
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    cell.font = Font(bold=False)
                    cell.border = None

    return buffer