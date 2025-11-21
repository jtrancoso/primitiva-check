import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
SERVICE_ACCOUNT_FILE = "service_account.json"

# Convertimos la string "1,2,3" a un set {1, 2, 3}
MY_NUMBERS = set(map(int, os.getenv("MY_NUMBERS").split(",")))
REINTEGRO = int(os.getenv("REINTEGRO"))

RSS_URL = os.getenv("RSS_URL")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]