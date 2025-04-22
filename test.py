import requests

url = "https://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "application/rss+xml,application/xml",
    "Referer": "https://www.loteriasyapuestas.es/"
}

r = requests.get(url, headers=headers)
print("Status:", r.status_code)
print("Contenido:", r.text[:500])
