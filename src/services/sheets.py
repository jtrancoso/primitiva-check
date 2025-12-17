import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# Importamos configuración
from config.settings import SERVICE_ACCOUNT_FILE, SCOPES, SPREADSHEET_URL

# Celdas para el control de renovación (debajo de los datos estáticos en K)
CELL_CYCLE_START = "K18"     # Fecha inicio del ciclo actual
CELL_NEXT_RENEWAL = "K19"    # Fecha próxima renovación


def get_sheet_client():
    """Conecta a Google Sheets y devuelve la hoja y credenciales."""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_url(SPREADSHEET_URL).sheet1, creds


def to_google_sheets_date(dt):
    """Convierte datetime a serial de Excel/Sheets."""
    epoch = datetime(1899, 12, 30)
    delta = dt - epoch
    return float(delta.days) + (delta.seconds / 86400)


def append_sorteo_row(sheet, row_data):
    """
    Añade una fila de sorteo al final de la tabla A:H.
    Usa table_range para NO afectar las columnas J-K.
    """
    sheet.append_row(row_data, table_range="A:H")


def get_renewal_dates(sheet):
    """Lee las fechas de renovación desde M2 y M3."""
    start_date = None
    renewal_date = None
    
    try:
        start_str = sheet.acell(CELL_CYCLE_START).value
        if start_str:
            start_date = datetime.strptime(start_str, "%d/%m/%Y")
    except (ValueError, AttributeError):
        pass

    try:
        renewal_str = sheet.acell(CELL_NEXT_RENEWAL).value
        if renewal_str:
            renewal_date = datetime.strptime(renewal_str, "%d/%m/%Y")
    except (ValueError, AttributeError):
        pass
        
    return start_date, renewal_date


def update_renewal_dates(sheet, start_date, renewal_date):
    """Actualiza las fechas de renovación en M2 y M3."""
    sheet.update(range_name=CELL_CYCLE_START, values=[[start_date.strftime("%d/%m/%Y")]])
    sheet.update(range_name=CELL_NEXT_RENEWAL, values=[[renewal_date.strftime("%d/%m/%Y")]])