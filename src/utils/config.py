import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")

API_BASE_URL = os.getenv("FOOTBALL_API_BASE_URL")
API_TOKEN = os.getenv("FOOTBALL_API_TOKEN")

BRONZE_PATH = DATA_PATH / "bronze" / "football_data"
SILVER_PATH = DATA_PATH / "silver" / "football_data"
