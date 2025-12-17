# 🧮 Primitiva Check

Script en Python para consultar automáticamente los resultados del sorteo de La Primitiva, registrar los aciertos en Google Sheets y crear recordatorios de renovación en Google Calendar.

---

## 🚀 Características

- **Scraping con Playwright** — Evita bloqueos de Cloudflare/Akamai usando modo headless stealth
- **Google Sheets** — Registra los sorteos con fecha, números, aciertos y premio real
- **Google Calendar** — Crea eventos de recordatorio para renovar el boleto cada 2 semanas
- **Notificaciones por email** — Te avisa si hay premio (3+ aciertos) o si la IP es bloqueada
- **Dockerizado** — Preparado para ejecutarse en Cloud Run Jobs o cualquier entorno con Docker

---

## ⚙️ Requisitos

- Python 3.9 o superior
- Cuenta de Google Cloud con un proyecto activo
- Google Sheet con acceso para la cuenta de servicio
- Calendario de Google con acceso para la cuenta de servicio
- Archivo `service_account.json` con permisos de Sheets y Calendar

---

## 🛠 Instalación

1. **Clona el repositorio:**

```bash
git clone https://github.com/jtrancoso/primitiva-check.git
cd primitiva-check/src
```

2. **Instala las dependencias:**

```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Configura tu archivo `.env`:**

```env
SPREADSHEET_ID=tu_id_de_google_sheet
MY_NUMBERS=tus_numeros
REINTEGRO=tu_reintegro
RSS_URL=https://www.loteriasyapuestas.es/es/la-primitiva/resultados/.formatoRSS
CALENDAR_ID=tu_email@gmail.com

# Notificaciones (opcional)
SMTP_EMAIL=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
NOTIFY_EMAIL=tu_email@gmail.com
```

4. **Coloca `service_account.json` en la carpeta `src/`**

5. **Ejecuta:**

```bash
python main.py
```

---

## 📊 Estructura del Sheet

| Columna | Contenido                   |
| ------- | --------------------------- |
| A       | Fecha del sorteo            |
| B       | Números premiados           |
| C       | Complementario              |
| D       | Reintegro                   |
| E       | Nº de aciertos              |
| F       | Tipo de premio              |
| G       | Importe del premio (€)      |
| H       | Coste del boleto (€)        |
| K18     | Fecha inicio del ciclo      |
| K19     | Próxima fecha de renovación |

---

## 📧 Notificaciones

El script envía emails automáticos cuando:

- 🎉 **Hay premio** (3+ aciertos) — Incluye categoría e importe real
- 🚨 **IP bloqueada** — Detecta bloqueos de Akamai/Cloudflare
- ❌ **Error crítico** — Problemas con el RSS o la conexión

---

## 🧾 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
