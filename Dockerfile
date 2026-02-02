# Cambiamos node:18 por node:22 que es la más actual y compatible
FROM node:22-alpine AS build

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

COPY .env .env

# Exponemos el puerto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "ai_backeng.main:app", "--host", "0.0.0.0", "--port", "8000"]
