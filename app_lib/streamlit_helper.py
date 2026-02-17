def highlight_total_row(row):
    if row.name == "Total":
        return [
            """
            font-weight: 600;
            background-color: rgba(127, 127, 127, 0.12);
            border-top: 1px solid rgba(127, 127, 127, 0.4);
            """
            ] * len(row)
    return [""] * len(row)