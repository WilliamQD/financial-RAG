import pandas as pd
from io import BytesIO
from dropbox_client import download_file


def load_merged() -> pd.DataFrame:
    data = download_file('/data/merged.csv')
    return pd.read_csv(BytesIO(data))


def load_sample() -> pd.DataFrame:
    data = download_file('/data/sample/sample_1000gvkey_bybatch.csv')
    return pd.read_csv(BytesIO(data))

def load_comp_total() -> pd.DataFrame:
    data = download_file('/data/financials/comp_total_q.pqt')
    data_df = pd.read_parquet(BytesIO(data))
    data_df['gvkey'] = data_df['gvkey'].str.lstrip('0').astype(int)
    return data_df

def filter_test_entries(df: pd.DataFrame, dir_file: str) -> pd.DataFrame:
    """
    Given a dataframe, remove the training and validation entries and return the rest.
    A csv diretory is expected to contain gvkey, fyear, and split columns.
    Exmaple: 
    12345, 2020, train
    67890, 2021, validation
    """
    splits = pd.read_csv(dir_file)
    
    # build a set of all (gvkey,fyear) that are train or validation
    bad = set(
        zip(
            splits.loc[splits['split'].isin(['train','validation']), 'gvkey'],
            splits.loc[splits['split'].isin(['train','validation']), 'fyear'],
        )
    )
    # keep only rows whose (gvkey,fyear) tuple is NOT in that set
    return df[~df[['gvkey','fyear']].apply(tuple, axis=1).isin(bad)]
