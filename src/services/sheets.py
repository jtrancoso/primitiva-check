import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from gspread_formatting import cellFormat, numberFormat, format_cell_range

# Importamos configuración
from config.settings import SERVICE_ACCOUNT_FILE, SCOPES, SPREADSHEET_URL

def get_sheet_client():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_url(SPREADSHEET_URL).sheet1, creds

def to_google_sheets_date(dt):
    """Convierte datetime a serial de Excel"""
    epoch = datetime(1899, 12, 30)
    delta = dt - epoch
    return float(delta.days) + (delta.seconds / 86400)

def get_renewal_dates(sheet):
    """Lee K10 y K11"""
    try:
        start_str = sheet.acell('K10').value
        start_date = datetime.strptime(start_str, "%d/%m/%Y") if start_str else None
    except:
        start_date = None

    try:
        end_str = sheet.acell('K11').value
        end_date = datetime.strptime(end_str, "%d/%m/%Y") if end_str else None
    except:
        end_date = None
        
    return start_date, end_date

def update_renewal_info(sheet, new_start_date, new_renewal_date):
    """Escribe las fechas y formatea K11"""
    
    # 1. K10 (Texto plano)
    sheet.update(range_name='K10', values=[[new_start_date.strftime('%d/%m/%Y')]])

    # 2. K11 (Serial para que sea Fecha real)
    serial_date = to_google_sheets_date(new_renewal_date)
    sheet.update(range_name='K11', values=[[serial_date]])

    # 3. Formato visual centrado
    fmt = cellFormat(
        numberFormat=numberFormat(type='DATE', pattern='dd/mm/yyyy'),
        horizontalAlignment='CENTER'
    )
    format_cell_range(sheet, 'K11', fmt)