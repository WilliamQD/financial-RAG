import requests
from dropbox import Dropbox
from config import DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN


def get_new_access_token() -> str:
    """Exchange refresh token for a new access token."""
    token_url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": DROPBOX_REFRESH_TOKEN,
        "client_id": DROPBOX_APP_KEY,
        "client_secret": DROPBOX_APP_SECRET,
    }
    resp = requests.post(token_url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_dropbox_client() -> Dropbox:
    token = get_new_access_token()
    return Dropbox(token)


def download_file(path: str) -> bytes:
    dbx = get_dropbox_client()
    _, res = dbx.files_download(path)
    return res.content