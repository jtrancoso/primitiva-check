import re
from datetime import datetime
from bs4 import BeautifulSoup

def parse_result(entry):
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

    return date, set(numbers), bonus, reintegro