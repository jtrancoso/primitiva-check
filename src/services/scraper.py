from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random


def get_rss_feed(url):
    """
    Obtiene el feed RSS de la Primitiva usando Playwright.
    
    Returns:
        tuple: (entries, was_blocked)
            - entries: lista de diccionarios con title y description
            - was_blocked: True si se detectó bloqueo de IP
    """
    ts = datetime.now().strftime("[%H:%M:%S]")
    print(f"{ts} 🕷️  Modo Stealth 2.0: Activando 'Headless New'...")
    
    try:
        with sync_playwright() as p:
            # --- EL TRUCO MAESTRO ---
            # 1. Le decimos a Playwright que NO es headless (para que no active sus flags de robot)
            # 2. Le pasamos '--headless=new' en args (para que Chrome se oculte usando el motor nuevo)
            browser = p.chromium.launch(
                headless=False,  # <--- IMPORTANTE: Dejar en False
                args=[
                    "--headless=new",  # El modo indetectable real
                    "--no-sandbox",
                    "--disable-dev-shm-usage",  # Importante para Docker/Cloud
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars"
                ]
            )
            
            # Contexto con User Agent de Chrome real
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="es-ES",
                timezone_id="Europe/Madrid"
            )
            
            page = context.new_page()

            # Scripts extra para borrar huellas de robot
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Navegación
            print(f"{ts} ➡️ Navegando a: {url}")
            response = page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            # Pequeña pausa aleatoria humana
            time.sleep(random.uniform(3, 5))

            content = page.content()
            status = response.status if response else 0
            print(f"{ts} 📡 Estado HTTP: {status}")

            browser.close()

            # Verificación de bloqueo
            blocked_indicators = [
                "Access Denied",
                "Request blocked",
                "Pardon Our Interruption",
                "Just a moment",  # Cloudflare
                "Please Wait",
            ]
            
            is_blocked = status == 403 or any(indicator in content for indicator in blocked_indicators)
            
            if is_blocked:
                print(f"{ts} 🚨 BLOQUEO DETECTADO. Estado: {status}")
                print(f"{ts} Contenido parcial:\n{content[:300]}")
                return [], True

            # Parseo
            soup = BeautifulSoup(content, "xml")
            items = soup.find_all("item")

            if not items:
                print(f"{ts} ⚠️ XML vacío o malformado. Inicio:\n{content[:300]}")
                return [], False

            entries = []
            for item in items:
                title = item.title.get_text(strip=True)
                description = item.description.get_text()
                entries.append({"title": title, "description": description})
            
            print(f"{ts} ✅ Obtenidos {len(entries)} sorteos del RSS")
            return entries, False

    except Exception as e:
        print(f"❌ Error en Scraper: {e}")
        return [], False