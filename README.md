# 🧮 Primitiva Check

Script en Python para consultar automáticamente los resultados del sorteo de La Primitiva y registrar los aciertos en una hoja de cálculo de Google Sheets.

---

## 🚀 Características

- Consulta el feed oficial de resultados vía RSS.
- Extrae la combinación ganadora, el número complementario y el reintegro.
- Compara con tu combinación personal y evalúa el tipo de premio.
- Registra los resultados en Google Sheets con formato automático.
- Añade colores condicionales según número de aciertos y tipo de premio.
- Se puede automatizar con `cron` en una máquina local o una VM de GCP.

---

## ⚙️ Requisitos

- Python 3.7 o superior.
- Cuenta de Google Cloud con un proyecto activo.
- Una hoja de cálculo de Google Sheets creada.
- Archivo de credenciales `service_account.json` con acceso a esa hoja.
- Archivo `.env` con tus datos personales del sorteo.

---

## 🛠 Instalación

1. **Clona el repositorio:**

```bash
git clone https://github.com/jtrancoso/primitiva-check.git
cd primitiva-check
```

2. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

3. **Configura tu archivo `.env`:**

Crea un archivo `.env` en la raíz del proyecto con este contenido:

```env
SPREADSHEET_ID=tu_id_de_google_sheet
MY_NUMBERS=1,2,3,4,5,6
REINTEGRO=7
```

4. **Coloca `service_account.json` en la raíz del proyecto.**

---

## 🖥️ Ejecución manual

```bash
python main.py
```

---

## ☁️ Ejecución automática en Google Cloud VM

### 1. Asegúrate de tener configurado Python y las dependencias:

```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt
```

### 2. Establece la zona horaria de la VM a Madrid (opcional pero recomendable):

```bash
sudo timedatectl set-timezone Europe/Madrid
```

### 3. Crea un cron job:

```bash
crontab -e
```

Y añade esta línea (ajustando las rutas a la carpeta donde tengas el proyecto):

```bash
30 22 * * 1,4,6 cd /home/usuario/primitiva-check && /usr/bin/python3 main.py >> log.txt 2>&1
```

Esto ejecutará el script los **lunes, jueves y sábados a las 22:30** (hora local), registrando el resultado en `log.txt`.

---

## 🧪 Test local

Puedes ejecutar el script manualmente para asegurarte de que todo funciona:

```bash
python main.py
```

---

## 🧾 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
