# Definir la imagen base de Python
FROM python:3.12

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias a la imagen
COPY requirements.txt .

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
COPY . .

# Exponer el puerto donde el servicio estará disponible
EXPOSE 5050

# Definir el comando que se ejecutará para iniciar el servicio
CMD ["python", "user.py"]
