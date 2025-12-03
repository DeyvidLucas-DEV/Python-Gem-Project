# Sistema de Publicações Acadêmicas - GEM

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

API RESTful para gerenciamento de publicações acadêmicas, membros e subgrupos de pesquisa. Desenvolvida com FastAPI, SQLAlchemy e PostgreSQL.

## Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Local](#instalação-local)
- [Configuração](#configuração)
- [Deploy em Produção](#deploy-em-produção)
- [Comandos do Servidor](#comandos-do-servidor)
- [Armazenamento de Arquivos](#armazenamento-de-arquivos)
- [API Endpoints](#api-endpoints)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Troubleshooting](#troubleshooting)
- [Contribuindo](#contribuindo)

---

## Características

- **API RESTful** completa com FastAPI
- **Async/Await** para operações de banco de dados de alta performance
- **PostgreSQL** com suporte a tipos nativos e relacionamentos complexos
- **Armazenamento de arquivos** no sistema de arquivos (não Base64)
- **URLs assinadas** com expiração para acesso seguro aos arquivos
- **Validação de dados** com Pydantic v2
- **Documentação automática** com Swagger/OpenAPI e ReDoc
- **Testes automatizados** com pytest e pytest-asyncio
- **Docker Compose** para containerização completa
- **CI/CD** com GitHub Actions
- **Nginx** como reverse proxy
- **CORS** configurável
- **Proteção contra path traversal** em uploads

---

## Tecnologias

| Tecnologia | Uso |
|------------|-----|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web moderno e rápido |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | ORM com suporte async |
| [PostgreSQL](https://www.postgresql.org/) | Banco de dados relacional |
| [Pydantic v2](https://docs.pydantic.dev/) | Validação de dados |
| [asyncpg](https://github.com/MagicStack/asyncpg) | Driver PostgreSQL async |
| [aiofiles](https://github.com/Tinche/aiofiles) | Operações de arquivo async |
| [Docker](https://www.docker.com/) | Containerização |
| [Nginx](https://nginx.org/) | Reverse proxy |
| [GitHub Actions](https://github.com/features/actions) | CI/CD |
| [Pytest](https://pytest.org/) | Framework de testes |
| [Uvicorn](https://www.uvicorn.org/) | Servidor ASGI |
| [Dozzle](https://dozzle.dev/) | Visualização de logs |

---

## Estrutura do Projeto

```
Python-Gem-Project/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── files.py         # Endpoint de arquivos (URLs assinadas)
│   │       │   ├── membros.py
│   │       │   ├── publicacoes.py
│   │       │   └── subgrupos.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py                # Configurações (env vars)
│   │   ├── database.py              # Conexão com banco
│   │   └── storage.py               # Armazenamento de arquivos
│   ├── crud/
│   │   ├── base.py
│   │   ├── membro.py
│   │   ├── publicacao.py
│   │   └── subgrupo.py
│   ├── models/
│   │   ├── base.py
│   │   ├── membro.py
│   │   ├── publicacao.py
│   │   ├── subgrupo.py
│   │   └── associations.py
│   ├── schemas/
│   │   ├── membro.py
│   │   ├── publicacao.py
│   │   └── subgrupo.py
│   └── utils/
│       └── exceptions.py
├── alembic/                          # Migrations do banco
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── test_membro.py
│   ├── test_publicacao.py
│   └── test_subgrupo.py
├── .github/
│   └── workflows/
│       └── deploy.yml                # Pipeline CI/CD
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── alembic.ini
└── pytest.ini
```

---

## Pré-requisitos

### Desenvolvimento Local
- Python 3.11+
- PostgreSQL 15+
- pip

### Servidor de Produção
- Ubuntu 20.04+ ou similar
- Docker e Docker Compose
- Git
- Acesso SSH

---

## Instalação Local

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/Python-Gem-Project.git
cd Python-Gem-Project
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 5. Execute as migrations

```bash
alembic upgrade head
```

### 6. Inicie o servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Acesse:**
- API: http://localhost:8000
- Swagger: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

---

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gem_db

# Segurança (OBRIGATÓRIO em produção)
SECRET_KEY=sua-chave-secreta-muito-longa-e-segura-aqui

# Armazenamento de Arquivos
UPLOADS_PATH=/var/data/uploads

# API
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Publicações Acadêmicas
VERSION=1.0.0

# CORS (origens permitidas)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Paginação
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Configuração do Banco de Dados

```sql
-- Criar banco de dados
CREATE DATABASE gem_db;

-- Criar usuário (opcional)
CREATE USER gem_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE gem_db TO gem_user;
```

---

## Deploy em Produção

### Preparação do Servidor

#### 1. Instalar Docker

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y
```

#### 2. Clonar o Projeto

```bash
sudo mkdir -p /var/www/gem-project
sudo chown $USER:$USER /var/www/gem-project
cd /var/www/gem-project
git clone https://github.com/seu-usuario/Python-Gem-Project.git .
```

#### 3. Criar Diretório de Uploads

```bash
sudo mkdir -p /var/data/gem-project/uploads
sudo chown -R 1000:1000 /var/data/gem-project/uploads
```

#### 4. Configurar Variáveis de Ambiente

```bash
nano .env
```

Conteúdo:

```env
DATABASE_URL=postgresql+asyncpg://usuario:senha@db:5432/gem_db
SECRET_KEY=gere-uma-chave-secreta-com-openssl-rand-hex-32
UPLOADS_PATH=/var/data/uploads

# Se a senha tiver $, escape com $$ (ex: senha$123 -> senha$$123)
```

> **IMPORTANTE:** Se a senha do banco tiver caractere `$`, use `$$` para escapar.
> Exemplo: `!$GEM2026e` deve ser `!$$GEM2026e`

#### 5. Iniciar o Projeto

```bash
docker compose up -d
```

#### 6. Executar Migrations

```bash
docker exec gem-api alembic upgrade head
```

---

## Comandos do Servidor

### Comandos Essenciais

| Ação | Comando |
|------|---------|
| **Iniciar projeto** | `docker compose up -d` |
| **Parar projeto** | `docker compose down` |
| **Reiniciar projeto** | `docker compose restart` |
| **Ver status** | `docker compose ps` |
| **Ver logs (tempo real)** | `docker logs -f gem-api` |
| **Ver logs (últimas 100 linhas)** | `docker logs --tail 100 gem-api` |

### Atualização do Projeto

Após fazer push no GitHub:

```bash
cd /var/www/gem-project
git pull origin main
docker compose down && docker compose up -d
```

> **Nota:** Se você configurou GitHub Actions, o deploy é automático após push na branch `main`.

### Migrations

```bash
# Aplicar migrations pendentes
docker exec gem-api alembic upgrade head

# Ver histórico de migrations
docker exec gem-api alembic history

# Criar nova migration
docker exec gem-api alembic revision --autogenerate -m "descrição"
```

### Banco de Dados

```bash
# Acessar PostgreSQL
docker exec -it gem-db psql -U usuario -d gem_db

# Backup do banco
docker exec gem-db pg_dump -U usuario gem_db > backup.sql

# Restaurar backup
cat backup.sql | docker exec -i gem-db psql -U usuario -d gem_db
```

### Gerenciamento de Containers

```bash
# Ver todos os containers
docker ps -a

# Parar todos os containers
docker stop $(docker ps -aq)

# Remover todos os containers
docker rm $(docker ps -aq)

# Limpar imagens não utilizadas
docker image prune -f

# Ver uso de disco
docker system df
```

---

## Armazenamento de Arquivos

### Arquitetura

O sistema utiliza **armazenamento em sistema de arquivos** em vez de Base64 no banco de dados para melhor performance.

```
/var/data/gem-project/uploads/
├── membros/
│   └── abc123-uuid.jpg
├── subgrupos/
│   ├── bg/
│   │   └── def456-uuid.png
│   └── icon/
│       └── ghi789-uuid.svg
└── publicacoes/
    └── jkl012-uuid.webp
```

### URLs Assinadas

Os arquivos são protegidos com **URLs assinadas com expiração** (1 hora por padrão).

**Formato da URL:**
```
https://seu-dominio.com/api/v1/files/membros/uuid.jpg?token=abc123&expires=1699999999
```

**Segurança:**
- Token HMAC-SHA256 gerado com `SECRET_KEY`
- Expiração configurável (padrão: 1 hora)
- Proteção contra path traversal
- Whitelist de extensões permitidas

### Upload de Arquivos

```bash
# Upload de imagem de membro
curl -X POST "https://api.exemplo.com/api/v1/membros/1/upload-foto" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@foto.jpg"

# Upload de capa de publicação
curl -X POST "https://api.exemplo.com/api/v1/publicacoes/1/upload-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@capa.png"
```

### Consumo no Frontend

```javascript
// Exemplo React/JavaScript
const response = await fetch('/api/v1/membros/1');
const membro = await response.json();

// A URL já vem assinada com token e expiração
const imagemUrl = membro.foto_url;
// => "/api/v1/files/membros/abc123.jpg?token=xyz&expires=1699999999"

// Usar diretamente no componente
<img src={imagemUrl} alt={membro.nome} />
```

---

## API Endpoints

### Membros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/membros/` | Listar membros |
| GET | `/api/v1/membros/{id}` | Obter membro |
| POST | `/api/v1/membros/` | Criar membro |
| PUT | `/api/v1/membros/{id}` | Atualizar membro |
| DELETE | `/api/v1/membros/{id}` | Deletar membro |
| POST | `/api/v1/membros/{id}/upload-foto` | Upload foto |

**Campos do Membro:**
- `nome` - Nome completo
- `email` - E-mail
- `linkedin` - URL do LinkedIn
- `lattes` - URL do Currículo Lattes
- `foto_url` - URL assinada da foto

### Publicações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/publicacoes/` | Listar publicações |
| GET | `/api/v1/publicacoes/{id}` | Obter publicação |
| POST | `/api/v1/publicacoes/` | Criar publicação |
| PUT | `/api/v1/publicacoes/{id}` | Atualizar publicação |
| DELETE | `/api/v1/publicacoes/{id}` | Deletar publicação |
| POST | `/api/v1/publicacoes/{id}/upload-image` | Upload capa |
| GET | `/api/v1/publicacoes/tipos/` | Listar tipos |
| GET | `/api/v1/publicacoes/estatisticas/` | Estatísticas |

**Tipos de Publicação:**
- `materia`, `dissertacao`, `livro`, `tese`, `capitulo_livro`, `policy_brief`, `Artigo`

**Campos da Publicação:**
- `title` - Título
- `description` - Descrição
- `type` - Tipo da publicação
- `year` - Data
- `link` - Link externo (href)
- `capa_url` - URL assinada da capa

### Subgrupos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/subgrupos/` | Listar subgrupos |
| GET | `/api/v1/subgrupos/{id}` | Obter subgrupo |
| POST | `/api/v1/subgrupos/` | Criar subgrupo |
| PUT | `/api/v1/subgrupos/{id}` | Atualizar subgrupo |
| DELETE | `/api/v1/subgrupos/{id}` | Deletar subgrupo |
| POST | `/api/v1/subgrupos/{id}/upload-bg` | Upload imagem de fundo |
| POST | `/api/v1/subgrupos/{id}/upload-icon` | Upload ícone |
| POST | `/api/v1/subgrupos/{id}/upload-infografico` | Upload infográfico |

**Campos do Subgrupo:**
- `nome` - Nome do subgrupo
- `descricao` - Descrição
- `bg_url` - URL da imagem de fundo (capa)
- `icon_url` - URL do ícone
- `infograficos` - Lista de infográficos

### Arquivos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/files/{path}` | Servir arquivo (requer token) |

**Parâmetros obrigatórios:**
- `token` - Token de assinatura HMAC
- `expires` - Timestamp de expiração

---

## Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Com verbosidade
pytest -v

# Com cobertura
pytest --cov=app --cov-report=html

# Teste específico
pytest tests/test_publicacao.py -v

# Testes em paralelo
pytest -n auto
```

### Estrutura de Testes

```python
# tests/conftest.py - Fixtures compartilhadas
# tests/test_membro.py - Testes de membros
# tests/test_publicacao.py - Testes de publicações
# tests/test_subgrupo.py - Testes de subgrupos
```

---

## CI/CD

### GitHub Actions

O projeto usa GitHub Actions para CI/CD automático.

**Arquivo:** `.github/workflows/deploy.yml`

**Pipeline:**
1. **Test** - Roda pytest em ambiente isolado
2. **Deploy** - SSH para servidor, pull e restart

### Configurar Secrets

No GitHub, vá em Settings > Secrets and Variables > Actions:

| Secret | Descrição |
|--------|-----------|
| `SSH_PRIVATE_KEY` | Chave SSH privada para acessar o servidor |
| `SSH_HOST` | IP ou domínio do servidor |
| `SSH_USER` | Usuário SSH (ex: root) |

### Deploy Manual

Se preferir deploy manual:

```bash
ssh user@servidor
cd /var/www/gem-project
git pull origin main
docker compose down && docker compose up -d
docker exec gem-api alembic upgrade head
```

---

## Troubleshooting

### Problemas Comuns

#### Porta 80 em uso

```bash
# Ver o que está usando a porta
sudo lsof -i :80

# Parar containers antigos
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
```

#### Erro de autenticação no banco

Se a senha tem `$`, escape com `$$`:

```env
# Errado
DATABASE_URL=postgresql+asyncpg://user:senha$123@db:5432/gem_db

# Correto
DATABASE_URL=postgresql+asyncpg://user:senha$$123@db:5432/gem_db
```

#### Coluna não existe (após migration)

```bash
docker exec gem-api alembic upgrade head
```

#### Container não inicia

```bash
# Ver logs de erro
docker logs gem-api

# Reconstruir imagem
docker compose build --no-cache
docker compose up -d
```

#### Permissão negada em uploads

```bash
sudo chown -R 1000:1000 /var/data/gem-project/uploads
sudo chmod -R 755 /var/data/gem-project/uploads
```

#### URL de arquivo expirada

As URLs expiram após 1 hora. O frontend deve solicitar novamente os dados da API para obter uma URL atualizada.

### Logs Úteis

```bash
# API
docker logs -f gem-api

# Banco de dados
docker logs -f gem-db

# Nginx
docker logs -f gem-nginx

# Todos os serviços
docker compose logs -f
```

### Monitoramento com Dozzle

Se configurado, acesse Dozzle para visualização de logs:
- URL: `http://seu-servidor:9999`

---

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

### Padrões de Código

- PEP 8 para estilo Python
- Type hints em todas as funções
- Testes para novas funcionalidades
- Cobertura mínima de 80%

---

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## Contato

GEM - Grupo de Estudos e Pesquisas

Para suporte, abra uma issue no repositório.
