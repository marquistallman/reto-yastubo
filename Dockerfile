# Usamos una imagen oficial ligera de Python
# '3.11-slim' es un buen balance entre tamaño y compatibilidad
FROM python:3.11-slim

# Evita que Python genere archivos .pyc (bytecode)
ENV PYTHONDONTWRITEBYTECODE=1
# Asegura que los logs de Python se envíen directamente a la terminal del contenedor
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /code

# Copiamos las dependencias primero para aprovechar la caché de capas de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente
COPY . .

# (Opcional pero recomendado) Crear un usuario no-root por seguridad
RUN adduser --disabled-password --gecos '' appuser

# Asignar permisos al usuario appuser sobre el directorio de trabajo
RUN chown -R appuser:appuser /code

USER appuser

# Exponemos el puerto 8000 para que VS Code sepa dónde conectarse
EXPOSE 8000

# Configurar PYTHONPATH para asegurar que se encuentren los módulos
ENV PYTHONPATH=/code

# Comando para ejecutar la aplicación.
# Ejecutar como módulo asegura que sys.path esté configurado correctamente
CMD ["python", "-m", "uvicorn", "app.modules.module_a_identity.main:app", "--host", "0.0.0.0", "--port", "8000"]
