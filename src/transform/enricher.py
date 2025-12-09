import gender_guesser.detector as gender
import pandas as pd

from log_config import get_logger

def fill_gender(df):
    d = gender.Detector()
    logger = get_logger(module_name=__name__)

    # iterate through df and fill missing gender cols
    for idx, row in df.iterrows():
        if pd.isna(row['gender']) or row['gender'].strip() == "":
            gen = d.get_gender(row['name'].split()[0])
            logger.debug(f"Guessed gender for {row['name']}: {gen}")

            # only fill results that are certain
            if gen in ['male', 'female']:
                df.at[idx, 'gender'] = gen[0].upper()
            elif gen in ['mostly_male', 'mostly_female']:
                df.at[idx, 'gender'] = gen[7].upper()

    return df