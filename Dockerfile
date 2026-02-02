FROM python:3.11-slim

# Evita prompts interactivos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (importante para sentence-transformers)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos el código
COPY ai_backeng ./ai_backeng

#COPY .env .env

# Exponemos el puerto
EXPOSE 8000

CMD ["uvicorn", "ai_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
