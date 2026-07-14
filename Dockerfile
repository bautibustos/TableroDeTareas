FROM python:3.12.3-slim-bookworm

# Directorio de trabajo 
WORKDIR /app

# copiar requerimientos
COPY requeriments.txt .

# ejecutar instalacion de requerimientos
RUN pip install --no-cache-dir -r requeriments.txt

# copiar proyecto
COPY . .

# posteo de la imagen 
EXPOSE 8000

# comando para correr la app 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]