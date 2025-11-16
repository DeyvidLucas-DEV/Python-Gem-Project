# Sistema de Publicações Acadêmicas

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

API RESTful para gerenciamento de publicações acadêmicas, membros e subgrupos de pesquisa. Desenvolvida com FastAPI, SQLAlchemy e PostgreSQL.

## 📋 Índice

- [Características](#-características)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Testes](#-testes)
- [Docker](#-docker)
- [CI/CD](#-cicd)
- [Contribuindo](#-contribuindo)

## ✨ Características

- **API RESTful** completa com FastAPI
- **Async/Await** para operações de banco de dados de alta performance
- **PostgreSQL** com suporte a tipos nativos e relacionamentos complexos
- **Validação de dados** com Pydantic v2
- **Documentação automática** com Swagger/OpenAPI e ReDoc
- **Testes automatizados** com pytest e pytest-asyncio
- **Docker** para containerização
- **CI/CD** com Jenkins
- **CORS** configurável
- **Tratamento de exceções** centralizado
- **Paginação** em todos os endpoints de listagem

## 🛠 Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)** - ORM com suporte async
- **[PostgreSQL](https://www.postgresql.org/)** - Banco de dados relacional
- **[Pydantic v2](https://docs.pydantic.dev/)** - Validação de dados
- **[asyncpg](https://github.com/MagicStack/asyncpg)** - Driver PostgreSQL async
- **[Pytest](https://pytest.org/)** - Framework de testes
- **[Docker](https://www.docker.com/)** - Containerização
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI

## 📁 Estrutura do Projeto

```
Python-Gem-Project/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # Endpoints da API
│   │       │   ├── membros.py
│   │       │   ├── publicacoes.py
│   │       │   └── subgrupos.py
│   │       └── api.py          # Router principal
│   ├── core/
│   │   ├── config.py           # Configurações
│   │   └── database.py         # Conexão com banco
│   ├── crud/
│   │   ├── base.py             # Operações CRUD base
│   │   ├── membro.py
│   │   ├── publicacao.py
│   │   └── subgrupo.py
│   ├── models/
│   │   ├── base.py             # Modelo base
│   │   ├── membro.py
│   │   ├── publicacao.py
│   │   ├── subgrupo.py
│   │   └── associations.py     # Tabelas de associação
│   ├── schemas/
│   │   ├── membro.py           # Schemas Pydantic
│   │   ├── publicacao.py
│   │   └── subgrupo.py
│   └── utils/
│       └── exceptions.py       # Tratamento de exceções
├── tests/
│   ├── conftest.py             # Configuração de testes
│   ├── test_membro.py
│   ├── test_publicacao.py
│   └── test_subgrupo.py
├── main.py                     # Ponto de entrada
├── requirements.txt            # Dependências
├── Dockerfile                  # Imagem Docker
├── docker-compose.yml          # Orquestração
├── Jenkinsfile                 # Pipeline CI/CD
└── pytest.ini                  # Configuração pytest
```

## 📦 Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <repository-url>
cd Python-Gem-Project
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv .venv
```

### 3. Ative o ambiente virtual

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 4. Instale as dependências

```bash
python3 -m pip install -r requirements.txt
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gem_db

# API
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Publicações Acadêmicas
VERSION=1.0.0
DESCRIPTION=API para gerenciamento de publicações, membros e subgrupos

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Paginação
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Configuração do Banco de Dados

1. Crie o banco de dados PostgreSQL:

```sql
CREATE DATABASE gem_db;
```

2. Execute as migrations (se disponíveis):

```bash
alembic upgrade head
```

## 🎯 Uso

### Desenvolvimento

Inicie o servidor de desenvolvimento com hot-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Ou execute diretamente:

```bash
python main.py
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/api/v1/docs
- **Documentação ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

### Produção

Use Gunicorn com Uvicorn workers:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📡 API Endpoints

### Membros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/membros/` | Listar todos os membros |
| GET | `/api/v1/membros/{id}` | Obter membro por ID |
| POST | `/api/v1/membros/` | Criar novo membro |
| PUT | `/api/v1/membros/{id}` | Atualizar membro |
| DELETE | `/api/v1/membros/{id}` | Deletar membro |
| GET | `/api/v1/membros/search/avancada` | Busca avançada |

### Publicações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/publicacoes/` | Listar todas as publicações |
| GET | `/api/v1/publicacoes/{id}` | Obter publicação por ID |
| POST | `/api/v1/publicacoes/` | Criar nova publicação |
| PUT | `/api/v1/publicacoes/{id}` | Atualizar publicação |
| DELETE | `/api/v1/publicacoes/{id}` | Deletar publicação |
| GET | `/api/v1/publicacoes/tipos/` | Listar tipos disponíveis |
| POST | `/api/v1/publicacoes/{id}/upload-image` | Upload de imagem |
| GET | `/api/v1/publicacoes/estatisticas/` | Estatísticas |

**Tipos de Publicação:**
- `materia`
- `dissertacao`
- `livro`
- `tese`
- `capitulo_livro`
- `policy_brief`
- `Artigo`

### Subgrupos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/subgrupos/` | Listar todos os subgrupos |
| GET | `/api/v1/subgrupos/{id}` | Obter subgrupo por ID |
| POST | `/api/v1/subgrupos/` | Criar novo subgrupo |
| PUT | `/api/v1/subgrupos/{id}` | Atualizar subgrupo |
| DELETE | `/api/v1/subgrupos/{id}` | Deletar subgrupo |

### Exemplo de Requisição

```bash
# Criar uma publicação
curl -X 'POST' \
  'http://localhost:8000/api/v1/publicacoes/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Título da Publicação",
  "description": "Descrição detalhada",
  "type": "materia",
  "year": "2025-11-16",
  "autor_ids": [1],
  "subgrupo_ids": [1]
}'
```

## 🧪 Testes

Execute todos os testes:

```bash
pytest
```

Execute com cobertura:

```bash
pytest --cov=app --cov-report=html
```

Execute testes específicos:

```bash
# Testar apenas publicações
pytest tests/test_publicacao.py

# Testar um teste específico
pytest tests/test_publicacao.py::test_create_publicacao_tipo_materia -v
```

Executar testes com output detalhado:

```bash
pytest -v -s
```

## 🐳 Docker

### Build da Imagem

```bash
docker build -t gem-api .
```

### Executar com Docker Compose

```bash
docker-compose up -d
```

Isso iniciará:
- API na porta 8000
- PostgreSQL na porta 5432
- Nginx (se configurado)

### Parar os containers

```bash
docker-compose down
```

### Ver logs

```bash
docker-compose logs -f api
```

## 🔄 CI/CD

O projeto utiliza Jenkins para CI/CD. O pipeline inclui:

1. **Checkout** - Clone do repositório
2. **Build** - Construção da imagem Docker
3. **Test** - Execução dos testes
4. **Deploy** - Deploy para ambiente de produção

Veja o arquivo `Jenkinsfile` para detalhes da configuração.

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- Siga a PEP 8 para estilo de código Python
- Use type hints em todas as funções
- Documente todas as funções e classes
- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes acima de 80%

## 📝 Notas de Desenvolvimento

### Modelos e Relacionamentos

O projeto possui três modelos principais:

1. **Membro** - Representa membros/autores
2. **Publicacao** - Representa publicações acadêmicas
3. **Subgrupo** - Representa subgrupos de pesquisa

**Relacionamentos Many-to-Many:**
- Publicações ↔ Membros (autores)
- Publicações ↔ Subgrupos

### Paginação

Todos os endpoints de listagem suportam paginação:

```
GET /api/v1/publicacoes/?skip=0&limit=20
```

### Filtros

Endpoints suportam filtros dinâmicos:

```
GET /api/v1/publicacoes/?year=2025&autor_id=1
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- GEM - Grupo de Estudos e Pesquisas

## 📧 Contato

Para questões e suporte, abra uma issue no repositório.

---

Desenvolvido com ❤️ usando FastAPI
