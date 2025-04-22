# Imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto estándar que usará Cloud Run
EXPOSE 8080

# Usa gunicorn para lanzar la app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:update_primitiva"]