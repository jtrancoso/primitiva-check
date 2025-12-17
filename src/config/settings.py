import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
SERVICE_ACCOUNT_FILE = "service_account.json"

# Tus números de la Primitiva
MY_NUMBERS = set(map(int, os.getenv("MY_NUMBERS").split(",")))
REINTEGRO = int(os.getenv("REINTEGRO"))

# URL del RSS de resultados
RSS_URL = os.getenv("RSS_URL")

# Scopes de Google APIs
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]