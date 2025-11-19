# Quick Start - Início Rápido

## Iniciar o Projeto em 3 Passos

### 1️⃣ Instalar Dependências

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Configurar Banco de Dados

```bash
# Aplicar migrations
alembic upgrade head

# Criar usuário administrador inicial
python create_admin.py
```

### 3️⃣ Iniciar Servidor

**Opção A - Script Automático:**
```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

**Opção B - Comando Manual:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Acessar a API

✅ **API está rodando em:** http://localhost:8000

- 📚 **Documentação Interativa:** http://localhost:8000/docs
- 📖 **Documentação ReDoc:** http://localhost:8000/redoc
- 💚 **Health Check:** http://localhost:8000/health
- 📊 **Dashboard de Saúde:** http://localhost:8000/health/ui

## Primeiro Acesso

### 1. Fazer Login (obter token)

**Via Swagger UI:**
1. Acesse http://localhost:8000/docs
2. Vá até `POST /api/v1/auth/login`
3. Use as credenciais:
   - **username:** `admin`
   - **password:** `admin123`
4. Copie o `access_token` da resposta

**Via curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Autenticar no Swagger

1. Clique no botão **"Authorize"** no topo da página
2. Digite: `Bearer SEU_TOKEN_AQUI`
3. Clique em **"Authorize"**
4. Agora você pode acessar todos os endpoints protegidos!

### 3. Criar Recursos

Agora você pode criar membros, publicações e subgrupos usando os endpoints protegidos.

## Exemplo de Uso Completo

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# 2. Criar um membro
curl -X POST "http://localhost:8000/api/v1/membros/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Dr. João Silva",
    "descricao": "Pesquisador em IA",
    "experiencia": "10 anos de experiência em Machine Learning"
  }'

# 3. Listar membros (público - não precisa de token)
curl "http://localhost:8000/api/v1/membros/"
```

## Estrutura de Autenticação

### Endpoints Públicos (sem autenticação)
- ✅ `GET /api/v1/membros/` - Listar membros
- ✅ `GET /api/v1/publicacoes/` - Listar publicações
- ✅ `GET /api/v1/subgrupos/` - Listar subgrupos
- ✅ `POST /api/v1/auth/register` - Registrar novo usuário
- ✅ `POST /api/v1/auth/login` - Fazer login

### Endpoints Protegidos (requerem token JWT)
- 🔒 `POST /api/v1/membros/` - Criar membro
- 🔒 `PUT /api/v1/membros/{id}` - Atualizar membro
- 🔒 `DELETE /api/v1/membros/{id}` - Deletar membro
- 🔒 `POST /api/v1/publicacoes/` - Criar publicação
- 🔒 `PUT /api/v1/publicacoes/{id}` - Atualizar publicação
- 🔒 `DELETE /api/v1/publicacoes/{id}` - Deletar publicação
- 🔒 `POST /api/v1/subgrupos/` - Criar subgrupo
- 🔒 `PUT /api/v1/subgrupos/{id}` - Atualizar subgrupo
- 🔒 `DELETE /api/v1/subgrupos/{id}` - Deletar subgrupo

## Comandos Úteis

```bash
# Ver migrations aplicadas
alembic current

# Criar novo usuário admin
python create_admin.py

# Executar testes
pytest

# Ver logs do servidor
uvicorn main:app --reload --log-level debug

# Parar o servidor
Ctrl + C
```

## Problemas Comuns

### ❌ Erro: "ModuleNotFoundError"
**Solução:** Ative o ambiente virtual e instale as dependências
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Erro: "Connection refused" no banco
**Solução:** Verifique se o PostgreSQL está rodando e as credenciais estão corretas em `app/core/database.py`

### ❌ Erro: "Token inválido"
**Solução:** Faça login novamente para obter um novo token (tokens expiram em 24 horas)

### ❌ Erro: "401 Unauthorized"
**Solução:** Certifique-se de incluir o header `Authorization: Bearer SEU_TOKEN` nas requisições

## Próximos Passos

1. ✅ Altere a senha do admin após primeiro login
2. ✅ Configure o `SECRET_KEY` em produção (veja SETUP.md)
3. ✅ Crie usuários adicionais via `/api/v1/auth/register`
4. ✅ Explore a documentação completa em `/docs`

---

Para documentação completa, veja [SETUP.md](SETUP.md)
