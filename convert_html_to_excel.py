import pandas as pd
from pathlib import Path

def convert_raw_data_to_csvs():
    raw_agmark_download_dir = Path('downloads_agmark')
    # Return a list of regular files only, not directories
    file_list = [f for f in raw_agmark_download_dir.glob('**/*') if f.is_file()]

    for file in file_list:
        # Read the HTML table
        tables = pd.read_html(file)

        # Usually the first table is the one you want
        df = tables[0]

        # Save as CSV
        df.to_csv(f"excel_agmark/{file.stem}.csv", index=False)

def merge_csvs():
    agmark_excel_dir = Path('excel_agmark')
    # Return a list of regular files only, not directories
    file_list = [f for f in agmark_excel_dir.glob('**/*') if f.is_file()]

    tables = []
    for file in file_list:
        tables.append(pd.read_csv(file))

    pd.concat(tables).to_csv(f"excel_agmark/Cotton_FULL_DATA.csv", index=False)


if __name__ == "__main__":
    # convert_raw_data_to_csvs()
    merge_csvs()
