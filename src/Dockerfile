FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Navegador ya viene en la imagen base, pero aseguramos la instalación
RUN playwright install chromium

# Copiar código (NO incluir service_account.json aquí, irá por Secret Manager)
COPY config/ ./config/
COPY domain/ ./domain/
COPY services/ ./services/
COPY main.py .

# Variables de entorno para Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

CMD ["python", "main.py"]