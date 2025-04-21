import feedparser
import gspread
from flask import Flask
from google.oauth2.service_account import Credentials
from gspread_formatting import *
from datetime import datetime
import re
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIG
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
SERVICE_ACCOUNT_FILE = "service_account.json"
MY_NUMBERS = set(map(int, os.getenv("MY_NUMBERS").split(",")))
REINTEGRO = 3
RSS_URL = "https://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# FLASK APP
app = Flask(__name__)

def parse_result(entry_title):
    date_match = re.search(r"La Primitiva - (.*?):", entry_title)
    date_str = date_match.group(1).strip() if date_match else ""
    date = datetime.strptime(date_str, "%A, %d de %B de %Y").strftime("%Y-%m-%d") if date_str else ""

    numbers_match = re.search(r": ([\d\s]+) bonus", entry_title)
    numbers_str = numbers_match.group(1).strip() if numbers_match else ""
    numbers = list(map(int, numbers_str.split())) if numbers_str else []

    bonus_match = re.search(r"bonus: (\d+)", entry_title)
    bonus = int(bonus_match.group(1)) if bonus_match else None

    reintegro_match = re.search(r"Reintegro: (\d+)", entry_title)
    reintegro = int(reintegro_match.group(1)) if reintegro_match else None

    return date, set(numbers), bonus, reintegro

def calculate_match(numbers_sorteo):
    return len(MY_NUMBERS.intersection(numbers_sorteo))

def calculate_prize(matches, bonus_match ,reintegro_acertado):
    premios = {3: 8, 4: 50, 5: 3000, 6: 1000000}
    premio = premios.get(matches, 0)
    
    if matches == 5 and bonus_match:
        return 50000  # ejemplo de premio 5+C
    if matches == 0 and reintegro_acertado:
        premio = 1
    return premio

def describir_premio(matches, bonus_match, reintegro_match):
    if matches == 6:
        return "6 Aciertos"
    elif matches == 5 and bonus_match:
        return "5 + Complementario"
    elif matches == 5:
        return "5 Aciertos"
    elif matches == 4:
        return "4 Aciertos"
    elif matches == 3:
        return "3 Aciertos"
    elif matches == 0 and reintegro_match:
        return "Reintegro"
    else:
        return "Sin premio"

def format(sheet):
    format_header = cellFormat(
        textFormat=textFormat(bold=True),
        backgroundColor=color(0.85, 0.92, 0.98),
        horizontalAlignment='CENTER'
    )
    format_date = cellFormat(
        numberFormat=numberFormat(type='DATE', pattern='dd/mm/yyyy'),
        horizontalAlignment='CENTER'
    )
    format_money = cellFormat(
        numberFormat=numberFormat(type='CURRENCY', pattern='€#,##0.00'),
        horizontalAlignment='RIGHT'
    )
    format_cell_range(sheet, 'A1:E1', format_header)
    format_cell_range(sheet, 'A2:A100', format_date)
    format_cell_range(sheet, 'D2:E100', format_money)
    format_centrado = cellFormat(horizontalAlignment='CENTER')
    format_cell_range(sheet, 'G2:G100', format_centrado)

@app.route("/update", methods=["GET"])
def update_primitiva():
    # 1. Leer el RSS
    feed = feedparser.parse(RSS_URL)
    
    print(feed)

    if not feed.entries:
        return "❌ No se encontraron resultados", 500

	 # 2. Autenticación con Sheets
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SPREADSHEET_URL).sheet1
    existing_dates = sheet.col_values(1)
    
    news = 0
    
	# 3. Recorrer los 7 sorteos más recientes
    for entry in feed.entries[:7]:
        try:
            date, numbers, bonus, reintegro = parse_result(entry.title)
            if date in existing_dates:
                print(f"⏭️ Sorteo del {date} ya existe, se omite")
                continue
            
            matches = calculate_match(numbers)
            bonus_match = bonus in MY_NUMBERS
            reintegro_match = reintegro in MY_NUMBERS
            prize = calculate_prize(matches, bonus_match, reintegro_match)
            tipo = describir_premio(matches, bonus_match, reintegro_match)
            cost = 1.0
            
            new_row = [date, " - ".join(map(str, sorted(numbers))), matches, prize, cost, bonus, tipo]
            sheet.append_row(new_row)
            news += 1
            print(f"✅ Añadido sorteo del {date}: {matches} aciertos, premio {prize}€")
        except Exception as e:
            print(f"⚠️ Error procesando una entrada: {e}")

    format(sheet)

    return f"✔️ Completado. Se añadieron {news} sorteos nuevos.", 200

if __name__ == "__main__":
    app.run(debug=True)