🧮 Primitiva Check
Automatiza la consulta de resultados de La Primitiva y registra tus aciertos en una hoja de cálculo de Google Sheets.

🚀 Características
Obtiene los resultados más recientes de La Primitiva desde el feed RSS oficial.

Compara los números ganadores con tus apuestas personales.

Registra los resultados en una hoja de cálculo de Google Sheets.

Formatea automáticamente la hoja con colores y estilos para facilitar la lectura.

Compatible con programación automática mediante cron.

📦 Requisitos
Python 3.7 o superior.

Cuenta de Google con acceso a Google Sheets.

Archivo de credenciales de cuenta de servicio (service_account.json).

Hoja de cálculo de Google Sheets creada y compartida con la cuenta de servicio.

🔧 Instalación
Clona el repositorio:

bash
Copiar
Editar
git clone https://github.com/jtrancoso/primitiva-check.git
cd primitiva-check
Crea y activa un entorno virtual (opcional pero recomendado):

bash
Copiar
Editar
python3 -m venv venv
source venv/bin/activate
Instala las dependencias:

bash
Copiar
Editar
pip install -r requirements.txt
Configura las variables de entorno:

Crea un archivo .env en la raíz del proyecto con el siguiente contenido:

env
Copiar
Editar
SPREADSHEET_ID=tu_id_de_hoja_de_calculo
MY_NUMBERS=1,2,3,4,5,6
REINTEGRO=7
SPREADSHEET_ID: ID de tu hoja de cálculo de Google Sheets.

MY_NUMBERS: Números de tu apuesta separados por comas.

REINTEGRO: Número de reintegro de tu apuesta.

Coloca el archivo de credenciales:

Descarga el archivo service_account.json desde Google Cloud Console y colócalo en la raíz del proyecto.

🖥️ Uso
Ejecuta el script manualmente:

bash
Copiar
Editar
python main.py
⏰ Automatización con cron
Para ejecutar el script automáticamente los días de sorteo (lunes, jueves y sábado) a las 22:30, añade la siguiente línea a tu crontab:

bash
Copiar
Editar
30 22 * * 1,4,6 /ruta/a/tu/python /ruta/a/tu/proyecto/main.py >> /ruta/a/tu/proyecto/log.txt 2>&1
Reemplaza /ruta/a/tu/python y /ruta/a/tu/proyecto/ con las rutas correspondientes en tu sistema.

📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.