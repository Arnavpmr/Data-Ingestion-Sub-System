from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

import os
from dotenv import load_dotenv

import pandas as pd

from log_config import get_logger

TABLE_NAME = "missing_persons"
DB_NAME = "missing_persons_db"

load_dotenv()

def load_to_postgres(df):
    logger = get_logger(module_name=__name__)
    # convert all age values to int in df
    logger.debug("Coercing age values to integers.")

    df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')
    records = df.to_dict(orient="records")

    engine = create_engine(f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{DB_NAME}")
    metadata = MetaData()

    missing = Table(
        TABLE_NAME,
        metadata,
        Column("name", String, nullable=False, primary_key=True, unique=True),
        Column("age", Integer),
        Column("gender", String),
        Column("date_missing", Date, nullable=False),
        Column("last_seen", String, nullable=False),
    )

    metadata.create_all(engine)  # or assume table exists

    stmt = pg_insert(missing).values(records)
    do_update = {c.name: stmt.excluded[c.name] for c in missing.c if c.name not in ('id',)}  # skip PK, or pick subset

    logger.debug("Preparing upsert statement for postgres.")
    stmt = stmt.on_conflict_do_update(
        index_elements=["name"],  # or constraint name
        set_=do_update,
    )

    with engine.begin() as conn:
        conn.execute(stmt)
        conn.commit()

    logger.info(f"Loaded {len(records)} records into postgres.")