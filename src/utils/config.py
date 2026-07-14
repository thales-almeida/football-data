import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("FOOTBALL_API_BASE_URL")
API_TOKEN = os.getenv("FOOTBALL_API_TOKEN")

BRONZE_PATH = "../data/bronze/football_data"
SILVER_PATH = "../data/silver/football_data"