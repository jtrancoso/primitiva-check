import os
from dotenv import load_dotenv

# Cargar .env solo si existe (en local)
load_dotenv()

# Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# Credenciales: archivo local o montado desde Secret Manager
# En Cloud Run, el secret se monta en /secrets/service_account.json
SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/secrets/service_account.json" if os.path.exists("/secrets/service_account.json") else "service_account.json"
)

# Tus números de la Primitiva
MY_NUMBERS = set(map(int, os.getenv("MY_NUMBERS").split(",")))
REINTEGRO = int(os.getenv("REINTEGRO"))

# URL del RSS de resultados
RSS_URL = os.getenv("RSS_URL")

# Google Calendar
CALENDAR_ID = os.getenv("CALENDAR_ID")

# Scopes de Google APIs
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]