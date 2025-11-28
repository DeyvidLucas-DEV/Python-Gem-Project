# Arquivo: Dockerfile
FROM python:3.13-slim

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copiar e instalar dependências primeiro (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de uploads
RUN mkdir -p /var/data/uploads

EXPOSE 8000

# Rodar com 4 workers (bom para 4 vCPU)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]