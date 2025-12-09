import gender_guesser.detector as gender
import pandas as pd

def fill_gender(df):
    d = gender.Detector()
    # iterate through df and fill missing gender cols
    for idx, row in df.iterrows():
        if pd.isna(row['gender']) or row['gender'].strip() == "":
            gen = d.get_gender(row['name'].split()[0])

            # only fill results that are certain
            if gen in ['male', 'female']:
                df.at[idx, 'gender'] = gen[0].upper()
            elif gen in ['mostly_male', 'mostly_female']:
                df.at[idx, 'gender'] = gen[7].upper()

    return df