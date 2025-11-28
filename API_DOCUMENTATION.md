# Documentação da API - Sistema de Publicações Acadêmicas

## Índice
- [Visão Geral](#visão-geral)
- [URL Base](#url-base)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
  - [Autenticação](#endpoints-de-autenticação)
  - [Membros](#endpoints-de-membros)
  - [Publicações](#endpoints-de-publicações)
  - [Subgrupos](#endpoints-de-subgrupos)
  - [Health Check](#health-check)
- [Modelos de Dados](#modelos-de-dados)
- [Códigos de Status HTTP](#códigos-de-status-http)
- [Exemplos de Integração](#exemplos-de-integração)

---

## Visão Geral

API RESTful para gerenciamento de publicações acadêmicas, membros e subgrupos de pesquisa. A API utiliza autenticação JWT (JSON Web Tokens) para endpoints protegidos.

**Versão:** 1.0.0

---

## URL Base

### Produção (VPS)
```
http://161.97.180.189/api/v1
```

### Desenvolvimento Local
```
http://localhost:8000/api/v1
```

---

## Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação. Endpoints que requerem autenticação estão marcados com 🔒.

### Como Autenticar

1. **Registrar um usuário** (`POST /auth/register`)
2. **Fazer login** (`POST /auth/login`) para obter um token
3. **Incluir o token** no header `Authorization` de todas as requisições protegidas:

```
Authorization: Bearer <seu_token_aqui>
```

### Expiração do Token

Os tokens JWT expiram em **1440 minutos (24 horas)**.

---

## Endpoints

### Endpoints de Autenticação

#### 1. Registrar Usuário
```http
POST /auth/register
```

Cria um novo usuário no sistema.

**Body (JSON):**
```json
{
  "email": "usuario@exemplo.com",
  "username": "usuario123",
  "password": "senha123456",
  "full_name": "João Silva"
}
```

**Campos:**
- `email` (string, obrigatório): Email válido
- `username` (string, obrigatório): Nome de usuário (mínimo 3, máximo 50 caracteres)
- `password` (string, obrigatório): Senha (mínimo 6 caracteres)
- `full_name` (string, opcional): Nome completo

**Resposta (201 Created):**
```json
{
  "id": 1,
  "email": "usuario@exemplo.com",
  "username": "usuario123",
  "full_name": "João Silva",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T10:30:00"
}
```

**Erros:**
- `400 Bad Request`: Email ou username já cadastrados

---

#### 2. Login
```http
POST /auth/login
```

Autentica um usuário e retorna um token JWT.

**Body (JSON):**
```json
{
  "username": "usuario123",
  "password": "senha123456"
}
```

**Resposta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Erros:**
- `401 Unauthorized`: Credenciais inválidas
- `403 Forbidden`: Usuário inativo

---

#### 3. Obter Usuário Atual 🔒
```http
GET /auth/me
```

Retorna as informações do usuário autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@exemplo.com",
  "username": "usuario123",
  "full_name": "João Silva",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T10:30:00"
}
```

---

### Endpoints de Membros

#### 1. Listar Membros
```http
GET /membros/
```

Retorna uma lista paginada de membros.

**Query Parameters:**
- `skip` (int, opcional, padrão: 0): Número de registros a pular
- `limit` (int, opcional, padrão: 20, máximo: 100): Limite de registros por página
- `q` (string, opcional): Termo de busca
- `subgrupo_id` (int, opcional): Filtrar por subgrupo

**Exemplo:**
```
GET /membros/?skip=0&limit=10&q=silva
```

**Resposta (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "Dr. João Silva",
      "descricao": "Pesquisador em Inteligência Artificial",
      "experiencia": "10 anos de experiência",
      "created_at": "2025-01-18T10:30:00",
      "updated_at": "2025-01-18T10:30:00",
      "subgrupos": [
        {
          "id": 1,
          "nome_grupo": "Grupo IA"
        }
      ],
      "publicacoes": [
        {
          "id": 1,
          "title": "Machine Learning Applications",
          "type": "Artigo"
        }
      ]
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 10,
  "has_next": true
}
```

---

#### 2. Criar Membro 🔒
```http
POST /membros/
```

Cria um novo membro.

**Headers:**
```
Authorization: Bearer <token>
```

**Body (JSON):**
```json
{
  "nome": "Dr. Maria Santos",
  "descricao": "Especialista em Machine Learning",
  "experiencia": "15 anos de experiência em IA"
}
```

**Campos:**
- `nome` (string, obrigatório): Nome do membro (1-255 caracteres)
- `descricao` (string, opcional): Descrição do membro
- `experiencia` (string, opcional): Experiência profissional

**Resposta (201 Created):**
```json
{
  "id": 2,
  "nome": "Dr. Maria Santos",
  "descricao": "Especialista em Machine Learning",
  "experiencia": "15 anos de experiência em IA",
  "created_at": "2025-01-18T10:35:00",
  "updated_at": "2025-01-18T10:35:00"
}
```

---

#### 3. Obter Membro por ID
```http
GET /membros/{id}
```

Retorna detalhes de um membro específico.

**Exemplo:**
```
GET /membros/1
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "nome": "Dr. João Silva",
  "descricao": "Pesquisador em Inteligência Artificial",
  "experiencia": "10 anos de experiência",
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T10:30:00",
  "subgrupos": [
    {
      "id": 1,
      "nome_grupo": "Grupo IA"
    }
  ],
  "publicacoes": [
    {
      "id": 1,
      "title": "Machine Learning Applications",
      "type": "Artigo"
    }
  ]
}
```

**Erros:**
- `404 Not Found`: Membro não encontrado

---

#### 4. Atualizar Membro 🔒
```http
PUT /membros/{id}
```

Atualiza um membro existente.

**Headers:**
```
Authorization: Bearer <token>
```

**Body (JSON):**
```json
{
  "nome": "Dr. João Silva Junior",
  "descricao": "Pesquisador Sênior em IA"
}
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "nome": "Dr. João Silva Junior",
  "descricao": "Pesquisador Sênior em IA",
  "experiencia": "10 anos de experiência",
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T11:00:00"
}
```

**Erros:**
- `404 Not Found`: Membro não encontrado

---

#### 5. Deletar Membro 🔒
```http
DELETE /membros/{id}
```

Remove um membro do sistema.

**Headers:**
```
Authorization: Bearer <token>
```

**Resposta (204 No Content)**

**Erros:**
- `404 Not Found`: Membro não encontrado

---

#### 6. Listar Subgrupos de um Membro
```http
GET /membros/{id}/subgrupos
```

Retorna todos os subgrupos aos quais o membro pertence.

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "nome_grupo": "Grupo de IA"
  },
  {
    "id": 2,
    "nome_grupo": "Grupo de Deep Learning"
  }
]
```

---

#### 7. Listar Publicações de um Membro
```http
GET /membros/{id}/publicacoes
```

Retorna todas as publicações de um membro.

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Machine Learning Applications",
    "type": "Artigo"
  }
]
```

---

#### 8. Upload de Foto do Membro 🔒
```http
POST /membros/{id}/upload-foto
```

Faz upload da foto do membro.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
- `file`: Arquivo de imagem (JPEG, PNG, etc.)

**Resposta (200 OK):**
```json
{
  "message": "Foto atualizada com sucesso"
}
```

**Erros:**
- `400 Bad Request`: Arquivo não é uma imagem
- `404 Not Found`: Membro não encontrado

---

#### 9. Upload de Background do Membro 🔒
```http
POST /membros/{id}/upload-background
```

Faz upload da imagem de background do membro.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
- `file`: Arquivo de imagem (JPEG, PNG, etc.)

**Resposta (200 OK):**
```json
{
  "message": "Background atualizado com sucesso"
}
```

---

#### 10. Buscar Membros por Nome
```http
GET /membros/search/nome
```

Busca membros pelo nome.

**Query Parameters:**
- `nome` (string, obrigatório): Nome ou parte do nome (mínimo 2 caracteres)
- `skip` (int, opcional): Número de registros a pular
- `limit` (int, opcional): Limite de registros por página

**Exemplo:**
```
GET /membros/search/nome?nome=silva&skip=0&limit=10
```

**Resposta (200 OK):**
```json
{
  "items": [...],
  "total": 5,
  "skip": 0,
  "limit": 10,
  "has_next": false
}
```

---

### Endpoints de Publicações

#### 1. Listar Publicações
```http
GET /publicacoes/
```

Retorna uma lista paginada de publicações.

**Query Parameters:**
- `skip` (int, opcional): Número de registros a pular
- `limit` (int, opcional): Limite de registros por página
- `q` (string, opcional): Termo de busca
- `tipo` (string, opcional): Filtrar por tipo (ver tipos disponíveis abaixo)
- `year` (int, opcional): Filtrar por ano
- `autor_id` (int, opcional): Filtrar por autor

**Tipos de Publicação:**
- `materia`
- `dissertacao`
- `livro`
- `tese`
- `capitulo_livro`
- `policy_brief`
- `Artigo`

**Exemplo:**
```
GET /publicacoes/?tipo=Artigo&year=2024&skip=0&limit=10
```

**Resposta (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Machine Learning Applications",
      "description": "Um estudo sobre aplicações de ML",
      "type": "Artigo",
      "year": "2024-01-15",
      "created_at": "2025-01-18T10:30:00",
      "updated_at": "2025-01-18T10:30:00",
      "autores": [
        {
          "id": 1,
          "nome": "Dr. João Silva"
        }
      ],
      "subgrupos": [
        {
          "id": 1,
          "nome_grupo": "Grupo IA"
        }
      ]
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 10,
  "has_next": true
}
```

---

#### 2. Criar Publicação 🔒
```http
POST /publicacoes/
```

Cria uma nova publicação.

**Headers:**
```
Authorization: Bearer <token>
```

**Body (JSON):**
```json
{
  "title": "Deep Learning na Saúde",
  "description": "Aplicações de deep learning em diagnósticos médicos",
  "type": "Artigo",
  "year": "2024-06-15",
  "autor_ids": [1, 2],
  "subgrupo_ids": [1]
}
```

**Campos:**
- `title` (string, obrigatório): Título da publicação (1-500 caracteres)
- `description` (string, opcional): Descrição da publicação
- `type` (string, obrigatório): Tipo da publicação (ver tipos disponíveis)
- `year` (string, opcional): Data da publicação (formato: AAAA-MM-DD)
- `autor_ids` (array, opcional): IDs dos autores
- `subgrupo_ids` (array, opcional): IDs dos subgrupos

**Resposta (201 Created):**
```json
{
  "id": 2,
  "title": "Deep Learning na Saúde",
  "description": "Aplicações de deep learning em diagnósticos médicos",
  "type": "Artigo",
  "year": "2024-06-15",
  "created_at": "2025-01-18T11:00:00",
  "updated_at": "2025-01-18T11:00:00",
  "autores": [
    {
      "id": 1,
      "nome": "Dr. João Silva"
    }
  ],
  "subgrupos": [
    {
      "id": 1,
      "nome_grupo": "Grupo IA"
    }
  ]
}
```

**Erros:**
- `400 Bad Request`: Autor ou subgrupo não encontrado

---

#### 3. Obter Publicação por ID
```http
GET /publicacoes/{id}
```

Retorna detalhes de uma publicação específica.

**Resposta (200 OK):**
```json
{
  "id": 1,
  "title": "Machine Learning Applications",
  "description": "Um estudo sobre aplicações de ML",
  "type": "Artigo",
  "year": "2024-01-15",
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T10:30:00",
  "autores": [...],
  "subgrupos": [...]
}
```

**Erros:**
- `404 Not Found`: Publicação não encontrada

---

#### 4. Atualizar Publicação 🔒
```http
PUT /publicacoes/{id}
```

Atualiza uma publicação existente.

**Headers:**
```
Authorization: Bearer <token>
```

**Body (JSON):**
```json
{
  "title": "Machine Learning Applications - 2ª Edição",
  "description": "Versão atualizada do estudo"
}
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "title": "Machine Learning Applications - 2ª Edição",
  "description": "Versão atualizada do estudo",
  "type": "Artigo",
  "year": "2024-01-15",
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T11:30:00",
  "autores": [...],
  "subgrupos": [...]
}
```

---

#### 5. Deletar Publicação 🔒
```http
DELETE /publicacoes/{id}
```

Remove uma publicação do sistema.

**Headers:**
```
Authorization: Bearer <token>
```

**Resposta (204 No Content)**

---

#### 6. Obter Tipos de Publicação
```http
GET /publicacoes/tipos/
```

Retorna todos os tipos de publicação disponíveis.

**Resposta (200 OK):**
```json
[
  "materia",
  "dissertacao",
  "livro",
  "tese",
  "capitulo_livro",
  "policy_brief",
  "Artigo"
]
```

---

#### 7. Busca Avançada
```http
GET /publicacoes/search/avancada
```

Busca avançada em publicações.

**Query Parameters:**
- `q` (string, obrigatório): Termo de busca (mínimo 2 caracteres)
- `tipo` (string, opcional): Filtrar por tipo
- `year` (int, opcional): Filtrar por ano
- `skip` (int, opcional): Número de registros a pular
- `limit` (int, opcional): Limite de registros por página

**Exemplo:**
```
GET /publicacoes/search/avancada?q=machine%20learning&tipo=Artigo&year=2024
```

**Resposta (200 OK):**
```json
{
  "items": [...],
  "total": 5,
  "skip": 0,
  "limit": 20,
  "has_next": false,
  "filters": {
    "query": "machine learning",
    "tipo": "Artigo",
    "year": 2024
  }
}
```

---

#### 8. Upload de Imagem da Publicação 🔒
```http
POST /publicacoes/{id}/upload-image
```

Faz upload da imagem da publicação.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
- `file`: Arquivo de imagem

**Resposta (200 OK):**
```json
{
  "message": "Imagem atualizada com sucesso"
}
```

---

#### 9. Estatísticas de Publicações
```http
GET /publicacoes/estatisticas/
```

Retorna estatísticas sobre as publicações.

**Resposta (200 OK):**
```json
{
  "total_publicacoes": 150,
  "por_tipo": {
    "materia": 20,
    "dissertacao": 30,
    "livro": 15,
    "tese": 25,
    "capitulo_livro": 10,
    "policy_brief": 5,
    "Artigo": 45
  },
  "tipos_disponiveis": [
    "materia",
    "dissertacao",
    "livro",
    "tese",
    "capitulo_livro",
    "policy_brief",
    "Artigo"
  ]
}
```

---

### Endpoints de Subgrupos

#### 1. Listar Subgrupos
```http
GET /subgrupos/
```

Retorna uma lista paginada de subgrupos.

**Query Parameters:**
- `skip` (int, opcional): Número de registros a pular
- `limit` (int, opcional): Limite de registros por página
- `q` (string, opcional): Termo de busca

**Resposta (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "nome_grupo": "Grupo de Inteligência Artificial",
      "descricao": "Pesquisas em IA e ML",
      "created_at": "2025-01-18T10:30:00",
      "updated_at": "2025-01-18T10:30:00",
      "icone_grupo_b64": "iVBORw0KGgoAAAANSUhEUgAA...",
      "bg_b64": "iVBORw0KGgoAAAANSUhEUgAA...",
      "membros": [
        {
          "id": 1,
          "nome": "Dr. João Silva"
        }
      ],
      "publicacoes": [
        {
          "id": 1,
          "title": "Machine Learning Applications",
          "type": "Artigo"
        }
      ]
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20,
  "has_next": false
}
```

**Nota:** Os campos `icone_grupo_b64` e `bg_b64` retornam imagens codificadas em Base64, prontas para uso em `<img src="data:image/png;base64,{icone_grupo_b64}" />`.

---

#### 2. Criar Subgrupo 🔒
```http
POST /subgrupos/
```

Cria um novo subgrupo.

**Headers:**
```
Authorization: Bearer <token>
```

**Body (JSON):**
```json
{
  "nome_grupo": "Grupo de Deep Learning",
  "descricao": "Pesquisas avançadas em redes neurais profundas"
}
```

**Campos:**
- `nome_grupo` (string, obrigatório): Nome do subgrupo (1-255 caracteres, deve ser único)
- `descricao` (string, opcional): Descrição do subgrupo

**Resposta (201 Created):**
```json
{
  "id": 2,
  "nome_grupo": "Grupo de Deep Learning",
  "descricao": "Pesquisas avançadas em redes neurais profundas",
  "created_at": "2025-01-18T11:00:00",
  "updated_at": "2025-01-18T11:00:00",
  "icone_grupo_b64": null,
  "bg_b64": null
}
```

**Erros:**
- `400 Bad Request`: Subgrupo com este nome já existe

---

#### 3. Obter Subgrupo por ID
```http
GET /subgrupos/{id}
```

Retorna detalhes de um subgrupo específico.

**Resposta (200 OK):**
```json
{
  "id": 1,
  "nome_grupo": "Grupo de Inteligência Artificial",
  "descricao": "Pesquisas em IA e ML",
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T10:30:00",
  "icone_grupo_b64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "bg_b64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "membros": [...],
  "publicacoes": [...]
}
```

**Erros:**
- `404 Not Found`: Subgrupo não encontrado

---

#### 4. Atualizar Subgrupo 🔒
```http
PUT /subgrupos/{id}
```

Atualiza um subgrupo existente.

**Headers:**
```
Authorization: Bearer <token>
```

**Body (JSON):**
```json
{
  "nome_grupo": "Grupo de IA Avançada",
  "descricao": "Pesquisas em IA de ponta"
}
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "nome_grupo": "Grupo de IA Avançada",
  "descricao": "Pesquisas em IA de ponta",
  "created_at": "2025-01-18T10:30:00",
  "updated_at": "2025-01-18T12:00:00",
  "icone_grupo_b64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "bg_b64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Erros:**
- `400 Bad Request`: Nome de subgrupo já existe
- `404 Not Found`: Subgrupo não encontrado

---

#### 5. Deletar Subgrupo 🔒
```http
DELETE /subgrupos/{id}
```

Remove um subgrupo do sistema.

**Headers:**
```
Authorization: Bearer <token>
```

**Resposta (204 No Content)**

---

#### 6. Adicionar Membro ao Subgrupo 🔒
```http
POST /subgrupos/{id}/membros/{membro_id}
```

Adiciona um membro a um subgrupo.

**Headers:**
```
Authorization: Bearer <token>
```

**Resposta (201 Created):**
```json
{
  "message": "Membro adicionado ao subgrupo com sucesso"
}
```

**Erros:**
- `400 Bad Request`: Membro já está associado a este subgrupo
- `404 Not Found`: Subgrupo ou membro não encontrado

---

#### 7. Remover Membro do Subgrupo 🔒
```http
DELETE /subgrupos/{id}/membros/{membro_id}
```

Remove um membro de um subgrupo.

**Headers:**
```
Authorization: Bearer <token>
```

**Resposta (204 No Content)**

**Erros:**
- `404 Not Found`: Associação não encontrada

---

#### 8. Listar Membros de um Subgrupo
```http
GET /subgrupos/{id}/membros
```

Retorna todos os membros de um subgrupo.

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "nome": "Dr. João Silva"
  },
  {
    "id": 2,
    "nome": "Dr. Maria Santos"
  }
]
```

---

#### 9. Upload de Ícone do Subgrupo 🔒
```http
POST /subgrupos/{id}/upload-icone
```

Faz upload do ícone do subgrupo.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
- `file`: Arquivo de imagem

**Resposta (200 OK):**
```json
{
  "message": "Ícone atualizado com sucesso"
}
```

---

#### 10. Upload de Background do Subgrupo 🔒
```http
POST /subgrupos/{id}/upload-background
```

Faz upload da imagem de background do subgrupo.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
- `file`: Arquivo de imagem

**Resposta (200 OK):**
```json
{
  "message": "Background atualizado com sucesso"
}
```

---

### Health Check

#### 1. Health Check Básico
```http
GET /health
```

Verifica o status da API e da conexão com o banco de dados.

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T12:00:00",
  "version": "1.0.0",
  "service": "Sistema de Publicações Acadêmicas",
  "checks": {
    "api": "healthy",
    "database": "healthy"
  }
}
```

---

#### 2. Health Check Detalhado
```http
GET /health?detailed=true
```

Retorna métricas detalhadas de infraestrutura.

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-18T12:00:00",
  "version": "1.0.0",
  "service": "Sistema de Publicações Acadêmicas",
  "checks": {
    "api": "healthy",
    "database": "healthy"
  },
  "metrics": {
    "cpu_percent": 15.5,
    "memory_percent": 45.2,
    "disk_percent": 60.3
  }
}
```

---

#### 3. Dashboard de Health
```http
GET /health/ui
```

Retorna um dashboard HTML para visualização de métricas.

---

## Modelos de Dados

### User (Usuário)

```typescript
interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}
```

---

### Membro

```typescript
interface Membro {
  id: number;
  nome: string;
  descricao: string | null;
  experiencia: string | null;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

interface MembroWithRelations extends Membro {
  subgrupos: SubgrupoSummary[];
  publicacoes: PublicacaoSummary[];
}

interface MembroSummary {
  id: number;
  nome: string;
}
```

---

### Publicação

```typescript
type TipoPublicacao =
  | "materia"
  | "dissertacao"
  | "livro"
  | "tese"
  | "capitulo_livro"
  | "policy_brief"
  | "Artigo";

interface Publicacao {
  id: number;
  title: string;
  description: string | null;
  type: TipoPublicacao;
  year: string | null; // formato: AAAA-MM-DD
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

interface PublicacaoWithRelations extends Publicacao {
  autores: MembroSummary[];
  subgrupos: SubgrupoSummary[];
}

interface PublicacaoSummary {
  id: number;
  title: string;
  type: TipoPublicacao;
}
```

---

### Subgrupo

```typescript
interface Subgrupo {
  id: number;
  nome_grupo: string;
  descricao: string | null;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  icone_grupo_b64: string | null; // Base64 encoded image
  bg_b64: string | null; // Base64 encoded image
}

interface SubgrupoWithRelations extends Subgrupo {
  membros: MembroSummary[];
  publicacoes: PublicacaoSummary[];
}

interface SubgrupoSummary {
  id: number;
  nome_grupo: string;
}
```

---

### Resposta Paginada

```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_next: boolean;
}
```

---

## Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 204 | No Content - Requisição bem-sucedida, sem conteúdo de retorno |
| 400 | Bad Request - Dados inválidos ou malformados |
| 401 | Unauthorized - Token ausente ou inválido |
| 403 | Forbidden - Acesso negado (usuário inativo ou sem permissão) |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Erro de validação |
| 500 | Internal Server Error - Erro no servidor |

---

## Exemplos de Integração

### React com Axios

#### Configuração Base

```javascript
// api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://161.97.180.189/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token automaticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

#### Exemplos de Uso

**1. Login e Armazenamento de Token**

```javascript
// authService.js
import api from './api';

export const authService = {
  async login(username, password) {
    try {
      const response = await api.post('/auth/login', {
        username,
        password,
      });

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao fazer login';
    }
  },

  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao registrar';
    }
  },

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao obter usuário';
    }
  },

  logout() {
    localStorage.removeItem('token');
  },
};
```

---

**2. Gerenciar Membros**

```javascript
// membroService.js
import api from './api';

export const membroService = {
  async getAll(params = {}) {
    try {
      const response = await api.get('/membros/', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar membros';
    }
  },

  async getById(id) {
    try {
      const response = await api.get(`/membros/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar membro';
    }
  },

  async create(membroData) {
    try {
      const response = await api.post('/membros/', membroData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao criar membro';
    }
  },

  async update(id, membroData) {
    try {
      const response = await api.put(`/membros/${id}`, membroData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao atualizar membro';
    }
  },

  async delete(id) {
    try {
      await api.delete(`/membros/${id}`);
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao deletar membro';
    }
  },

  async uploadFoto(id, file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post(`/membros/${id}/upload-foto`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao fazer upload da foto';
    }
  },

  async searchByNome(nome, params = {}) {
    try {
      const response = await api.get('/membros/search/nome', {
        params: { nome, ...params },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar membros';
    }
  },
};
```

---

**3. Gerenciar Publicações**

```javascript
// publicacaoService.js
import api from './api';

export const publicacaoService = {
  async getAll(params = {}) {
    try {
      const response = await api.get('/publicacoes/', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar publicações';
    }
  },

  async getById(id) {
    try {
      const response = await api.get(`/publicacoes/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar publicação';
    }
  },

  async create(publicacaoData) {
    try {
      const response = await api.post('/publicacoes/', publicacaoData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao criar publicação';
    }
  },

  async update(id, publicacaoData) {
    try {
      const response = await api.put(`/publicacoes/${id}`, publicacaoData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao atualizar publicação';
    }
  },

  async delete(id) {
    try {
      await api.delete(`/publicacoes/${id}`);
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao deletar publicação';
    }
  },

  async getTipos() {
    try {
      const response = await api.get('/publicacoes/tipos/');
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar tipos';
    }
  },

  async searchAvancada(query, filters = {}) {
    try {
      const response = await api.get('/publicacoes/search/avancada', {
        params: { q: query, ...filters },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro na busca avançada';
    }
  },

  async getEstatisticas() {
    try {
      const response = await api.get('/publicacoes/estatisticas/');
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar estatísticas';
    }
  },
};
```

---

**4. Gerenciar Subgrupos**

```javascript
// subgrupoService.js
import api from './api';

export const subgrupoService = {
  async getAll(params = {}) {
    try {
      const response = await api.get('/subgrupos/', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar subgrupos';
    }
  },

  async getById(id) {
    try {
      const response = await api.get(`/subgrupos/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar subgrupo';
    }
  },

  async create(subgrupoData) {
    try {
      const response = await api.post('/subgrupos/', subgrupoData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao criar subgrupo';
    }
  },

  async update(id, subgrupoData) {
    try {
      const response = await api.put(`/subgrupos/${id}`, subgrupoData);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao atualizar subgrupo';
    }
  },

  async delete(id) {
    try {
      await api.delete(`/subgrupos/${id}`);
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao deletar subgrupo';
    }
  },

  async addMembro(subgrupoId, membroId) {
    try {
      const response = await api.post(`/subgrupos/${subgrupoId}/membros/${membroId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao adicionar membro';
    }
  },

  async removeMembro(subgrupoId, membroId) {
    try {
      await api.delete(`/subgrupos/${subgrupoId}/membros/${membroId}`);
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao remover membro';
    }
  },

  async getMembros(id) {
    try {
      const response = await api.get(`/subgrupos/${id}/membros`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Erro ao buscar membros';
    }
  },
};
```

---

**5. Componente React de Exemplo**

```jsx
// MembrosPage.jsx
import React, { useState, useEffect } from 'react';
import { membroService } from './services/membroService';

function MembrosPage() {
  const [membros, setMembros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 10;

  useEffect(() => {
    loadMembros();
  }, [currentPage]);

  const loadMembros = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await membroService.getAll({
        skip: currentPage * limit,
        limit: limit,
      });

      setMembros(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || 'Erro ao carregar membros');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Deseja realmente deletar este membro?')) return;

    try {
      await membroService.delete(id);
      loadMembros(); // Recarregar lista
    } catch (err) {
      alert(err.message || 'Erro ao deletar membro');
    }
  };

  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;

  return (
    <div>
      <h1>Membros</h1>

      <div className="membros-list">
        {membros.map((membro) => (
          <div key={membro.id} className="membro-card">
            <h3>{membro.nome}</h3>
            <p>{membro.descricao}</p>
            <p><strong>Experiência:</strong> {membro.experiencia}</p>

            <div className="actions">
              <button onClick={() => handleDelete(membro.id)}>
                Deletar
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button
          onClick={() => setCurrentPage(page => Math.max(0, page - 1))}
          disabled={currentPage === 0}
        >
          Anterior
        </button>

        <span>
          Página {currentPage + 1} de {Math.ceil(total / limit)}
        </span>

        <button
          onClick={() => setCurrentPage(page => page + 1)}
          disabled={(currentPage + 1) * limit >= total}
        >
          Próxima
        </button>
      </div>
    </div>
  );
}

export default MembrosPage;
```

---

**6. Upload de Imagens**

```jsx
// UploadFotoMembro.jsx
import React, { useState } from 'react';
import { membroService } from './services/membroService';

function UploadFotoMembro({ membroId }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Selecione uma imagem');
      return;
    }

    try {
      setUploading(true);
      await membroService.uploadFoto(membroId, file);
      alert('Foto atualizada com sucesso!');
      setFile(null);
    } catch (err) {
      alert(err.message || 'Erro ao fazer upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h3>Upload de Foto</h3>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={uploading}
      />
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? 'Enviando...' : 'Enviar Foto'}
      </button>
    </div>
  );
}

export default UploadFotoMembro;
```

---

**7. Exibir Imagens Base64**

```jsx
// SubgrupoCard.jsx
import React from 'react';

function SubgrupoCard({ subgrupo }) {
  return (
    <div className="subgrupo-card">
      {subgrupo.icone_grupo_b64 && (
        <img
          src={`data:image/png;base64,${subgrupo.icone_grupo_b64}`}
          alt={`Ícone de ${subgrupo.nome_grupo}`}
          className="subgrupo-icone"
        />
      )}

      <h3>{subgrupo.nome_grupo}</h3>
      <p>{subgrupo.descricao}</p>

      {subgrupo.bg_b64 && (
        <div
          className="subgrupo-background"
          style={{
            backgroundImage: `url(data:image/png;base64,${subgrupo.bg_b64})`,
          }}
        />
      )}
    </div>
  );
}

export default SubgrupoCard;
```

---

## Documentação Interativa

A API possui documentação interativa gerada automaticamente pelo FastAPI:

- **Swagger UI:** `http://161.97.180.189/api/v1/docs`
- **ReDoc:** `http://161.97.180.189/api/v1/redoc`

Essas interfaces permitem testar todos os endpoints diretamente do navegador.

---

## Suporte

Para dúvidas ou problemas com a API, entre em contato com a equipe de desenvolvimento.

---

**Última atualização:** 18 de Janeiro de 2025
**Versão da API:** 1.0.0
