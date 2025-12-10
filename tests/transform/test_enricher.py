import pytest
import pandas as pd
from src.transform.enricher import fill_gender

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'name': ['Alice Johnson', 'Bob Smith', 'Randy', 'Dana White'],
        'gender': [None, '', None, 'F']
    })

def test_fill_gender_basic(sample_df):
    df = sample_df.copy()
    result = fill_gender(df)

    assert result.loc[0, 'gender'] in ['F', 'M']
    assert result.loc[1, 'gender'] in ['F', 'M']