import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file in the project root
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Environment-backed configuration
try:
    PINECONE_API_KEY      = os.environ["PINECONE_API_KEY"]
    OPENAI_API_KEY        = os.environ["OPENAI_API_KEY"]
    DROPBOX_APP_KEY       = os.environ["DBX_APP_KEY"]
    DROPBOX_APP_SECRET    = os.environ["DBX_APP_SECRET"]
    DROPBOX_REFRESH_TOKEN = os.environ["DBX_REFRESH_TOKEN"]
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e}")