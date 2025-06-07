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