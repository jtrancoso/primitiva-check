import re
from datetime import datetime
from bs4 import BeautifulSoup


def parse_prize_amount(amount_str: str) -> float:
    """
    Convierte un importe en formato español a float.
    
    Ejemplos:
        "8,00 €" → 8.0
        "1.854,41 €" → 1854.41
        "42.145,61 €" → 42145.61
    """
    if not amount_str:
        return 0.0
    
    # Quitar el símbolo € y espacios
    cleaned = amount_str.replace("€", "").replace(" ", "").strip()
    
    # Formato español: punto para miles, coma para decimales
    # Quitar puntos de miles y cambiar coma por punto
    cleaned = cleaned.replace(".", "").replace(",", ".")
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


# Mapeo de categorías del HTML a nuestros tipos de premio
CATEGORY_MAP = {
    "especial": "Especial (6 + R)",
    "1ª": "1ª (6 Aciertos)",
    "2ª": "2ª (5 + C)",
    "3ª": "3ª (5 Aciertos)",
    "4ª": "4ª (4 Aciertos)",
    "5ª": "5ª (3 Aciertos)",
    "reintegro": "Reintegro",
}


def parse_prize_table(soup):
    """
    Extrae la tabla de premios del HTML.
    
    Returns:
        dict: {tipo_premio: importe_str} ej: {"5ª (3 Aciertos)": "8,00 €"}
    """
    prizes = {}
    
    # Buscar la tabla de premios de la Primitiva (no la del Joker)
    table = soup.find("table", class_="tablaDetalle")
    if not table:
        return prizes
    
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:
            category_text = cells[0].get_text(strip=True).lower()
            prize_text = cells[2].get_text(strip=True)
            
            # Mapear la categoría
            for key, prize_type in CATEGORY_MAP.items():
                if key in category_text:
                    prizes[prize_type] = prize_text
                    break
    
    return prizes


def parse_result(entry):
    """
    Parsea una entrada del RSS y extrae los datos del sorteo.
    
    Returns:
        tuple: (date, numbers, bonus, reintegro, prizes)
            - date: datetime del sorteo
            - numbers: set de números ganadores
            - bonus: número complementario
            - reintegro: número de reintegro
            - prizes: dict con los importes por categoría
    """
    html = entry["description"]
    soup = BeautifulSoup(html, "html.parser")
    bold_tags = soup.find_all("b")
    
    if len(bold_tags) < 3:
        raise ValueError(f"Entrada incompleta: {entry['title']}")

    title = entry["title"]
    date_match = re.search(r"del (\d{1,2}) de (\w+) de (\d{4})", title, re.IGNORECASE)
    if not date_match:
        raise ValueError(f"Sin fecha en título: {title}")
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

    # Extraer tabla de premios
    prizes = parse_prize_table(soup)

    return date, set(numbers), bonus, reintegro, prizes