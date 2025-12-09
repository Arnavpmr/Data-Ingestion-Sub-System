import tabula
from pathlib import Path
from datetime import datetime
import pandas as pd

from log_config import get_logger

def parse_yosemite_pdf():
    logger = get_logger(module_name=__name__)

    cur_date = datetime.now().strftime("%Y-%m-%d")
    pdf_path = Path("data/raw/yosemite_pdf/missing_persons_yosemite.pdf")
    csv_path = Path(f"data/silver/yosemite_pdf/{cur_date}/missing_persons_yosemite.csv")

    # Read all tables in the PDF (most PDFs return a list of DataFrames)
    tables = tabula.read_pdf(str(pdf_path), pages='all', multiple_tables=False)

    if not tables:
        logger.error("No tables found in the PDF.")
        raise ValueError("No tables found in the PDF.")

    # If there's only one table:
    df = tables[0]

    # Clean up common formatting issues
    logger.debug("Cleaning up DataFrame formatting.")
    df.columns = [c.strip() for c in df.columns]
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Reorder columns and rename
    # merge first and last column into name column
    df['name'] = df['First'] + ' ' + df['Last']
    df = df.drop(columns=['First', 'Last'])
    desired_order = ["name", "date_missing", "last_seen"]

    df = df.rename(columns={'Last Known Point': 'last_seen', 'Date': 'date_missing'})
    df = df[[col for col in desired_order if col in df.columns]]

    # append Yosemite to every last_seen entry
    logger.debug("Appending 'Yosemite National Park' to last_seen entries.")
    df['last_seen'] = df['last_seen'].apply(lambda x: f"{x}, Yosemite National Park" if pd.notnull(x) else x)

    # Format date_missing to MM/DD/YYYY
    logger.debug("Formatting date_missing to MM/DD/YYYY.")
    df['date_missing'] = pd.to_datetime(df['date_missing'], errors='coerce').dt.strftime('%m/%d/%Y')

    # Save as CSV
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)

    logger.debug(f"Extracted table saved to: {csv_path}")
    logger.info(f"Parsed {len(df)} records from Yosemite PDF data.")