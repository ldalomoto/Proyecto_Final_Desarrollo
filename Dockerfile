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
<<<<<<< HEAD
=======
    libpq-dev \
>>>>>>> f1218efe1a87e65ff4ee58ccff100f53ea1ff1e0
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos el código
COPY ai_backeng ./ai_backeng
<<<<<<< HEAD
# COMETNAMOS POR PARA CI CD
# COPY .env .env
=======

COPY .env .env
>>>>>>> f1218efe1a87e65ff4ee58ccff100f53ea1ff1e0

# Exponemos el puerto
EXPOSE 8000

# Comando de arranque
<<<<<<< HEAD
CMD ["uvicorn", "ai_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
=======
CMD ["uvicorn", "ai_backeng.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> f1218efe1a87e65ff4ee58ccff100f53ea1ff1e0
