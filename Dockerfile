# Usamos una imagen oficial y ligera de Python
FROM python:3.13-slim

# Work Directory
WORKDIR /app

# Load dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code
COPY . .

# Service Expose
EXPOSE 8080

# App execution command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]