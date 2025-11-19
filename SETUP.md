# Guia de Instalação e Inicialização do Projeto

## Pré-requisitos

- Python 3.13+
- PostgreSQL instalado e rodando
- pip (gerenciador de pacotes Python)

## 1. Configuração do Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Linux/macOS:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

## 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

## 3. Configurar Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto (opcional, já que as configurações estão em `app/core/config.py`):

```env
DATABASE_URL=postgresql+asyncpg://root:!$GEM2026e@161.97.180.189:5432/gem_db
SECRET_KEY=seu_secret_key_aqui
```

⚠️ **IMPORTANTE**: Altere o `SECRET_KEY` em produção! Gere uma chave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Depois atualize o valor em `app/core/security.py` linha 8.

## 4. Aplicar Migrations do Banco de Dados

```bash
# Verificar migrations pendentes
alembic current

# Aplicar todas as migrations
alembic upgrade head
```

## 5. Iniciar o Servidor

### Modo Desenvolvimento (com hot-reload)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Produção

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Ou com Gunicorn:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 6. Acessar a API

- **API Base**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Dashboard de Saúde**: http://localhost:8000/health/ui

## 7. Criar Primeiro Usuário (Autenticação)

### Via curl:

```bash
# Registrar usuário
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "senha123",
    "full_name": "Administrador"
  }'

# Fazer login (obter token)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "senha123"
  }'
```

### Via Swagger UI:

1. Acesse http://localhost:8000/docs
2. Vá até `POST /api/v1/auth/register`
3. Clique em "Try it out"
4. Preencha os dados do usuário
5. Execute

## 8. Autenticar Requisições

### Obter Token:

Use o endpoint `POST /api/v1/auth/login` para obter o token JWT.

### Usar Token:

Adicione o header `Authorization` em todas as requisições protegidas:

```bash
curl -X POST "http://localhost:8000/api/v1/membros/" \
  -H "Authorization: Bearer SEU_TOKEN_JWT_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "descricao": "Pesquisador",
    "experiencia": "5 anos de experiência"
  }'
```

### No Swagger UI:

1. Faça login e copie o `access_token`
2. Clique no botão "Authorize" no topo da página
3. Digite: `Bearer SEU_TOKEN_AQUI`
4. Clique em "Authorize"
5. Agora pode acessar endpoints protegidos

## Estrutura de Endpoints

### Autenticação (Públicos)
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login (retorna token)
- `GET /api/v1/auth/me` - Dados do usuário atual (requer token)

### Membros
- `GET /api/v1/membros/` - Listar (público)
- `POST /api/v1/membros/` - Criar (protegido)
- `GET /api/v1/membros/{id}` - Buscar por ID (público)
- `PUT /api/v1/membros/{id}` - Atualizar (protegido)
- `DELETE /api/v1/membros/{id}` - Deletar (protegido)

### Publicações
- `GET /api/v1/publicacoes/` - Listar (público)
- `POST /api/v1/publicacoes/` - Criar (protegido)
- `GET /api/v1/publicacoes/{id}` - Buscar por ID (público)
- `PUT /api/v1/publicacoes/{id}` - Atualizar (protegido)
- `DELETE /api/v1/publicacoes/{id}` - Deletar (protegido)

### Subgrupos
- `GET /api/v1/subgrupos/` - Listar (público)
- `POST /api/v1/subgrupos/` - Criar (protegido)
- `GET /api/v1/subgrupos/{id}` - Buscar por ID (público)
- `PUT /api/v1/subgrupos/{id}` - Atualizar (protegido)
- `DELETE /api/v1/subgrupos/{id}` - Deletar (protegido)

## Troubleshooting

### Erro de conexão com banco de dados

Verifique se o PostgreSQL está rodando e as credenciais em `app/core/database.py` estão corretas.

### Erro "ModuleNotFoundError"

Certifique-se de que o ambiente virtual está ativado e as dependências foram instaladas:

```bash
pip install -r requirements.txt
```

### Migrations não aplicadas

```bash
# Ver status das migrations
alembic current

# Aplicar migrations
alembic upgrade head

# Criar nova migration (se necessário)
alembic revision --autogenerate -m "descrição da mudança"
```

### Token inválido ou expirado

Os tokens expiram após 24 horas. Faça login novamente para obter um novo token.

## Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Ver relatório de cobertura
open htmlcov/index.html
```

## Desenvolvimento

### Criar nova migration

```bash
alembic revision --autogenerate -m "descrição da alteração"
alembic upgrade head
```

### Reverter migration

```bash
alembic downgrade -1
```

### Ver histórico de migrations

```bash
alembic history
```
