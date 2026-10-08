# Imagen base ligera de Python
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código al contenedor
COPY . .

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para arrancar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]