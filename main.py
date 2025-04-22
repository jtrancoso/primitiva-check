import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import *
from datetime import datetime
import re
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# CONFIG
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
SERVICE_ACCOUNT_FILE = "service_account.json"
MY_NUMBERS = set(map(int, os.getenv("MY_NUMBERS").split(",")))
REINTEGRO = int(os.getenv("REINTEGRO"))
RSS_URL = "https://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_rss_feed(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.15; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Accept": "application/rss+xml,application/xml",
    "Referer": "https://www.loteriasyapuestas.es/"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")
    items = soup.find_all("item")

    entries = []
    for item in items:
        title = item.title.get_text(strip=True)
        description = item.description.get_text()
        entries.append({"title": title, "description": description})

    return entries

def parse_result(entry):
    html = entry["description"]
    soup = BeautifulSoup(html, "html.parser")
    bold_tags = soup.find_all("b")
    
    if len(bold_tags) < 3:
        raise ValueError(f"Entrada no válida (faltan datos): {entry['title']}")

    title = entry["title"]
    date_match = re.search(r"del (\d{1,2}) de (\w+) de (\d{4})", title, re.IGNORECASE)
    if not date_match:
        raise ValueError(f"No se pudo extraer la fecha del título: {title}")
    day, month_str, year = date_match.groups()

    months = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    month = months[month_str.lower()]
    date = datetime(int(year), month, int(day))

    raw_numbers = bold_tags[0].get_text(strip=True)
    numbers = list(map(int, raw_numbers.split(" - ")))

    bonus_text = bold_tags[1].get_text(strip=True)
    bonus = int(re.search(r"C\((\d+)\)", bonus_text).group(1))

    reintegro_text = bold_tags[2].get_text(strip=True)
    reintegro = int(re.search(r"R\((\d+)\)", reintegro_text).group(1))

    return date, set(numbers), bonus, reintegro

def calculate_match(numbers_sorteo):
    return len(MY_NUMBERS.intersection(numbers_sorteo))

def calculate_prize(matches, bonus_match, reintegro_match):
    return 1 if reintegro_match else 0

def set_prize(matches, bonus_match, reintegro_match):
    if matches == 6 and reintegro_match:
        return "Especial (6 + R)"
    elif matches == 6:
        return "1ª (6 Aciertos)"
    elif matches == 5 and bonus_match:
        return "2ª (5 + C)"
    elif matches == 5:
        return "3ª (5 Aciertos)"
    elif matches == 4:
        return "4ª (4 Aciertos)"
    elif matches == 3:
        return "5ª (3 Aciertos)"
    elif matches < 3 and reintegro_match:
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
        numberFormat=numberFormat(type='CURRENCY', pattern='##0.00,€#'),
        horizontalAlignment='RIGHT'
    )
    format_center = cellFormat(horizontalAlignment='CENTER')

    format_cell_range(sheet, 'A1:H1', format_header)
    format_cell_range(sheet, 'A2:A100', format_date)
    format_cell_range(sheet, 'B2:F100', format_center)
    format_cell_range(sheet, 'G2:H100', format_money)

    last_row = len(sheet.get_all_values())

    aciertos_rules = [
        ConditionalFormatRule(
            ranges=[GridRange(sheetId=sheet._properties['sheetId'], startRowIndex=1, endRowIndex=last_row, startColumnIndex=4, endColumnIndex=5)],
            booleanRule=BooleanRule(
                condition=BooleanCondition('NUMBER_LESS', ['3']),
                format=CellFormat(backgroundColor=Color(1, 0.9, 0.9))
            )
        ),
        ConditionalFormatRule(
            ranges=[GridRange(sheetId=sheet._properties['sheetId'], startRowIndex=1, endRowIndex=last_row, startColumnIndex=4, endColumnIndex=5)],
            booleanRule=BooleanRule(
                condition=BooleanCondition('NUMBER_GREATER_THAN_EQ', ['3']),
                format=CellFormat(backgroundColor=Color(0.8, 1, 0.8))
            )
        )
    ]

    tipo_rules = [
        ConditionalFormatRule(
            ranges=[GridRange(sheetId=sheet._properties['sheetId'], startRowIndex=1, endRowIndex=last_row, startColumnIndex=5, endColumnIndex=6)],
            booleanRule=BooleanRule(
                condition=BooleanCondition('TEXT_EQ', ['Sin premio']),
                format=CellFormat(backgroundColor=Color(1, 0.9, 0.9))
            )
        ),
        ConditionalFormatRule(
            ranges=[GridRange(sheetId=sheet._properties['sheetId'], startRowIndex=1, endRowIndex=last_row, startColumnIndex=5, endColumnIndex=6)],
            booleanRule=BooleanRule(
                condition=BooleanCondition('TEXT_EQ', ['Reintegro']),
                format=CellFormat(backgroundColor=Color(0.9, 0.9, 1))
            )
        ),
        ConditionalFormatRule(
            ranges=[GridRange(sheetId=sheet._properties['sheetId'], startRowIndex=1, endRowIndex=last_row, startColumnIndex=5, endColumnIndex=6)],
            booleanRule=BooleanRule(
                condition=BooleanCondition('TEXT_NOT_CONTAINS', ['Sin premio']),
                format=CellFormat(backgroundColor=Color(0.8, 1, 0.8))
            )
        )
    ]

    rules = get_conditional_format_rules(sheet)
    rules.clear()
    rules.extend(aciertos_rules + tipo_rules)
    rules.save()
    
	# Ordenar automáticamente por la columna A (fecha)
    sheet_id = sheet._properties["sheetId"]
    sort_request = {
        "requests": [
            {
                "sortRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,  # sin la cabecera
                        "startColumnIndex": 0,
                        "endColumnIndex": 8
                    },
                    "sortSpecs": [
                        {
                            "dimensionIndex": 0,  # columna A
                            "sortOrder": "DESCENDING"
                        }
                    ]
                }
            }
        ]
    }

    sheet.spreadsheet.batch_update(sort_request)

def update_primitiva():
    try:
        entries = get_rss_feed(RSS_URL)
        if not entries:
            print("❌ No se encontraron sorteos")
            return

        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SPREADSHEET_URL).sheet1
        existing_dates = sheet.col_values(1)

        for entry in entries[:1]:
            date, numbers, bonus, reintegro = parse_result(entry)
            date_str = date.strftime("%d/%m/%Y")

            if date_str in existing_dates:
                print(f"⏭️ Sorteo del {date_str} ya existe, se omite")
                return

            matches = calculate_match(numbers)
            bonus_match = bonus in MY_NUMBERS
            reintegro_match = reintegro == REINTEGRO
            prize = calculate_prize(matches, bonus_match, reintegro_match)
            prize_type = set_prize(matches, bonus_match, reintegro_match)
            cost = 1.0
            new_row = [date_str, " - ".join(map(str, sorted(numbers))), bonus, reintegro, matches, prize_type, prize, cost]
            sheet.append_row(new_row)
            format(sheet)

            print(f"✅ Añadido sorteo del {date_str}: {matches} aciertos, premio {prize}€")

    except Exception as e:
        print(f"❌ Error procesando: {e}")

if __name__ == "__main__":
    update_primitiva()
