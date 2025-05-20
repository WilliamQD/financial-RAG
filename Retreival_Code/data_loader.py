import pandas as pd
from io import BytesIO
from dropbox_client import download_csv


def load_merged() -> pd.DataFrame:
    data = download_csv('/data/merged.csv')
    return pd.read_csv(BytesIO(data))


def load_sample() -> pd.DataFrame:
    data = download_csv('/data/sample/sample_1000gvkey_bybatch.csv')
    return pd.read_csv(BytesIO(data))
