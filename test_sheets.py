import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import *
from datetime import datetime

# CONFIGURACIÓN
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1n-iWYLmyxKXTTUW2cJKeTKK4a9oWJ6x2RbT7v28JxFA"
SERVICE_ACCOUNT_FILE = "service_account.json"

# SCOPES necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def aplicar_formato(sheet):
    # Formato para cabecera
    format_cabecera = cellFormat(
        textFormat=textFormat(bold=True),
        backgroundColor=color(0.85, 0.92, 0.98),  # azul claro
        horizontalAlignment='CENTER'
    )

    # Formato para fecha
    format_fecha = cellFormat(
        numberFormat=numberFormat(type='DATE', pattern='dd/mm/yyyy'),
        horizontalAlignment='CENTER'
    )

    # Formato para moneda
    format_monedas = cellFormat(
        numberFormat=numberFormat(type='CURRENCY', pattern='€#,##0.00'),
        horizontalAlignment='RIGHT'
    )

    # Aplicar formatos
    format_cell_range(sheet, 'A1:E1', format_cabecera)  # Cabecera
    format_cell_range(sheet, 'A2:A100', format_fecha)   # Fechas
    format_cell_range(sheet, 'D2:E100', format_monedas) # Dinero y coste

def probar_conexion_y_formato():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SPREADSHEET_URL).sheet1

    print("✅ Conectado correctamente a la hoja")

    # Añadir fila de prueba
    hoy = datetime.now().strftime("%Y-%m-%d")
    fila_de_prueba = [hoy, "1 2 3 4 5 6", 2, 0, 1.0]
    sheet.append_row(fila_de_prueba)
    print("📝 Fila de prueba añadida")

    # Aplicar formato
    aplicar_formato(sheet)
    print("🎨 Formato aplicado correctamente")

if __name__ == "__main__":
    probar_conexion_y_formato()