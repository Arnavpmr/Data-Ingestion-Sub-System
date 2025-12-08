import tabula
from pathlib import Path
from datetime import datetime
import pandas as pd

if __name__ == "__main__":
    cur_date = datetime.now().strftime("%Y-%m-%d")
    pdf_path = Path("data/raw/yosemite_pdf/missing_persons_yosemite.pdf")
    csv_path = Path(f"data/silver/yosemite_pdf/{cur_date}/missing_persons_yosemite.csv")

    # Read all tables in the PDF (most PDFs return a list of DataFrames)
    tables = tabula.read_pdf(str(pdf_path), pages='all', multiple_tables=False)

    if not tables:
        raise ValueError("No tables found in the PDF.")

    # If there's only one table:
    df = tables[0]

    # Clean up common formatting issues (optional)
    df.columns = [c.strip() for c in df.columns]
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Reorder columns and rename if necessary (example order)
    # merge first and last col into name column
    df['name'] = df['First'] + ' ' + df['Last']
    df = df.drop(columns=['First', 'Last'])
    desired_order = ["name", "date_missing", "last_seen"]

    df = df.rename(columns={'Last Known Point': 'last_seen', 'Date': 'date_missing'})
    df = df[[col for col in desired_order if col in df.columns]]

    # append Yosemite to every last_seen entry
    df['last_seen'] = df['last_seen'].apply(lambda x: f"{x}, Yosemite National Park" if pd.notnull(x) else x)

    # Format date_missing to MM/DD/YYYY
    df['date_missing'] = pd.to_datetime(df['date_missing'], errors='coerce').dt.strftime('%m/%d/%Y')

    # Save as CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)

    print(f"Extracted table saved to: {csv_path}")