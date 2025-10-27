# Arquivo: Dockerfile

# 1. Imagem base Python 3.13 slim
FROM python:3.13-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /code

# 3. Copia APENAS o arquivo de dependências (da raiz)
COPY requirements.txt .

# 4. Instala as dependências (sem cache para economizar espaço)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia TODO o resto do código da aplicação (da raiz) para /code
#    O .dockerignore vai impedir que venv, __pycache__, .git etc. sejam copiados.
#    Isso copiará main.py e a pasta app/ para dentro de /code
COPY . .

# 6. Expõe a porta 8000 (a porta que Gunicorn/Uvicorn usará)
EXPOSE 8000

# 7. Comando para iniciar a aplicação quando o container rodar
#    Assume que em 'main.py' você tem uma variável 'app = FastAPI()'
#    Roda a partir do diretório /code onde main.py está.
#    --workers 4: Um bom número inicial de processos, ajuste conforme necessário.
#    --bind 0.0.0.0:8000: Ouve em todas as interfaces na porta 8000.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000"]