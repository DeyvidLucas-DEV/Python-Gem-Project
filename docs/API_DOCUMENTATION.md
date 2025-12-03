# Documentação Técnica da API - GEM

> Sistema de Publicações Acadêmicas
> Base URL: `https://seu-dominio.com/api/v1`

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Diagrama de Relacionamentos](#diagrama-de-relacionamentos)
4. [Entidades](#entidades)
   - [Membro](#membro)
   - [Subgrupo](#subgrupo)
   - [Publicação](#publicação)
5. [Endpoints](#endpoints)
   - [Membros](#endpoints-de-membros)
   - [Subgrupos](#endpoints-de-subgrupos)
   - [Publicações](#endpoints-de-publicações)
   - [Arquivos](#endpoints-de-arquivos)
   - [Autenticação](#endpoints-de-autenticação)
6. [Paginação](#paginação)
7. [Upload de Imagens](#upload-de-imagens)
8. [URLs Assinadas](#urls-assinadas)
9. [Exemplos de Integração Frontend](#exemplos-de-integração-frontend)
10. [Códigos de Erro](#códigos-de-erro)

---

## Visão Geral

A API GEM gerencia publicações acadêmicas, membros (pesquisadores) e subgrupos de pesquisa. Os três recursos principais possuem relacionamentos **Many-to-Many** entre si.

### Arquitetura de Recursos

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   MEMBRO    │◄─────►│  SUBGRUPO   │◄─────►│ PUBLICAÇÃO  │
│             │  N:N  │             │  N:N  │             │
│ - Pesquisador       │ - Grupo de  │       │ - Artigo    │
│ - Autor     │       │   Pesquisa  │       │ - Tese      │
│ - Contato   │       │ - Infográ-  │       │ - Livro     │
│             │       │   ficos     │       │ - etc.      │
└─────────────┘       └─────────────┘       └─────────────┘
       │                                           │
       └───────────────────────────────────────────┘
                         N:N (Autores)
```

### Relacionamentos

| Relação | Tipo | Descrição |
|---------|------|-----------|
| Membro ↔ Subgrupo | N:N | Um membro pode pertencer a vários subgrupos |
| Membro ↔ Publicação | N:N | Um membro pode ser autor de várias publicações |
| Subgrupo ↔ Publicação | N:N | Uma publicação pode pertencer a vários subgrupos |

---

## Autenticação

A API utiliza **JWT (JSON Web Token)** para autenticação. Endpoints que modificam dados (POST, PUT, DELETE) requerem autenticação.

### Obter Token

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=senha123
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Usar Token

Inclua o token no header de todas as requisições autenticadas:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Endpoints Públicos (sem autenticação)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/membros/` | Listar membros |
| GET | `/membros/{id}` | Obter membro |
| GET | `/subgrupos/` | Listar subgrupos |
| GET | `/subgrupos/{id}` | Obter subgrupo |
| GET | `/publicacoes/` | Listar publicações |
| GET | `/publicacoes/{id}` | Obter publicação |
| GET | `/publicacoes/tipos/` | Listar tipos |
| GET | `/files/{path}` | Servir arquivo (com token de URL) |

### Endpoints Protegidos (requer autenticação)

Todos os endpoints de criação (POST), atualização (PUT) e exclusão (DELETE).

---

## Diagrama de Relacionamentos

```
┌────────────────────────────────────────────────────────────────────┐
│                        BANCO DE DADOS                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐                           ┌──────────────┐       │
│  │   membros    │                           │   subgrupo   │       │
│  ├──────────────┤                           ├──────────────┤       │
│  │ id (PK)      │                           │ id (PK)      │       │
│  │ nome         │                           │ nome_grupo   │       │
│  │ descricao    │                           │ descricao    │       │
│  │ experiencia  │                           │ icone_path   │       │
│  │ email        │     ┌──────────────────┐  │ bg_path      │       │
│  │ linkedin     │◄───►│membros_subgrupos │◄►│ infograficos │       │
│  │ lattes       │     ├──────────────────┤  │              │       │
│  │ foto_path    │     │ membro_id (FK)   │  └──────────────┘       │
│  │ bg_path      │     │ subgrupo_id (FK) │         ▲               │
│  │ created_at   │     └──────────────────┘         │               │
│  │ updated_at   │                                  │               │
│  └──────────────┘                                  │               │
│         │                                          │               │
│         │     ┌──────────────────┐                 │               │
│         │     │publicacao_autores│                 │               │
│         │     ├──────────────────┤                 │               │
│         └────►│ publicacao_id(FK)│                 │               │
│               │ membro_id (FK)   │                 │               │
│               └──────────────────┘                 │               │
│                        │                           │               │
│                        ▼                           │               │
│               ┌──────────────┐    ┌────────────────────┐           │
│               │  publicacao  │◄──►│publicacao_subgrupos│           │
│               ├──────────────┤    ├────────────────────┤           │
│               │ id (PK)      │    │ publicacao_id (FK) │           │
│               │ title        │    │ subgrupo_id (FK)   │           │
│               │ description  │    └────────────────────┘           │
│               │ type         │                                     │
│               │ year         │                                     │
│               │ link_externo │                                     │
│               │ image_path   │                                     │
│               │ created_at   │                                     │
│               │ updated_at   │                                     │
│               └──────────────┘                                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Entidades

### Membro

Representa um pesquisador ou membro do grupo de estudos.

#### Campos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | integer | Auto | Identificador único |
| `nome` | string | Sim | Nome completo (max 255 chars) |
| `descricao` | string | Não | Descrição/biografia |
| `experiencia` | string | Não | Experiência profissional |
| `email` | string | Não | E-mail de contato |
| `linkedin` | string | Não | URL do perfil LinkedIn |
| `lattes` | string | Não | URL do Currículo Lattes |
| `foto_url` | string | Auto | URL assinada da foto (computed) |
| `bg_url` | string | Auto | URL assinada do background (computed) |
| `created_at` | datetime | Auto | Data de criação |
| `updated_at` | datetime | Auto | Data de atualização |
| `subgrupos` | array | Auto | Lista de subgrupos relacionados |
| `publicacoes` | array | Auto | Lista de publicações relacionadas |

#### Schema de Criação (MembroCreate)

```json
{
  "nome": "Dr. João Silva",
  "descricao": "Pesquisador em Ciência de Dados",
  "experiencia": "10 anos de experiência em machine learning",
  "email": "joao.silva@universidade.edu.br",
  "linkedin": "https://linkedin.com/in/joaosilva",
  "lattes": "http://lattes.cnpq.br/1234567890"
}
```

#### Schema de Resposta (MembroWithRelations)

```json
{
  "id": 1,
  "nome": "Dr. João Silva",
  "descricao": "Pesquisador em Ciência de Dados",
  "experiencia": "10 anos de experiência em machine learning",
  "email": "joao.silva@universidade.edu.br",
  "linkedin": "https://linkedin.com/in/joaosilva",
  "lattes": "http://lattes.cnpq.br/1234567890",
  "foto_url": "/api/v1/files/membros/photos/abc123.jpg?token=xyz&expires=1699999999",
  "bg_url": "/api/v1/files/membros/backgrounds/def456.jpg?token=xyz&expires=1699999999",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "subgrupos": [
    {"id": 1, "nome_grupo": "Inteligência Artificial"}
  ],
  "publicacoes": [
    {"id": 1, "title": "Machine Learning Aplicado", "type": "Artigo"}
  ]
}
```

---

### Subgrupo

Representa um subgrupo de pesquisa dentro do grupo GEM.

#### Campos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | integer | Auto | Identificador único |
| `nome_grupo` | string | Sim | Nome do subgrupo (único, max 255) |
| `descricao` | string | Não | Descrição do subgrupo |
| `icone_grupo_url` | string | Auto | URL assinada do ícone (computed) |
| `bg_url` | string | Auto | URL assinada da capa/background (computed) |
| `infograficos_urls` | array | Auto | Lista de URLs dos infográficos (computed) |
| `created_at` | datetime | Auto | Data de criação |
| `updated_at` | datetime | Auto | Data de atualização |
| `membros` | array | Auto | Lista de membros do subgrupo |
| `publicacoes` | array | Auto | Lista de publicações do subgrupo |

#### Schema de Criação (SubgrupoCreate)

```json
{
  "nome_grupo": "Inteligência Artificial",
  "descricao": "Subgrupo focado em pesquisas de IA e Machine Learning"
}
```

#### Schema de Resposta (SubgrupoWithRelations)

```json
{
  "id": 1,
  "nome_grupo": "Inteligência Artificial",
  "descricao": "Subgrupo focado em pesquisas de IA e Machine Learning",
  "icone_grupo_url": "/api/v1/files/subgrupos/icons/icon123.svg?token=xyz&expires=1699999999",
  "bg_url": "/api/v1/files/subgrupos/backgrounds/bg456.jpg?token=xyz&expires=1699999999",
  "infograficos_urls": [
    "/api/v1/files/subgrupos/infograficos/info1.png?token=abc&expires=1699999999",
    "/api/v1/files/subgrupos/infograficos/info2.png?token=def&expires=1699999999"
  ],
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "membros": [
    {"id": 1, "nome": "Dr. João Silva"},
    {"id": 2, "nome": "Dra. Maria Santos"}
  ],
  "publicacoes": [
    {"id": 1, "title": "Machine Learning Aplicado", "type": "Artigo"}
  ]
}
```

---

### Publicação

Representa uma publicação acadêmica (artigo, tese, livro, etc.).

#### Campos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | integer | Auto | Identificador único |
| `title` | string | Sim | Título da publicação (max 500) |
| `description` | string | Não | Descrição/resumo |
| `type` | enum | Sim | Tipo da publicação |
| `year` | date | Não | Data de publicação (YYYY-MM-DD) |
| `link_externo` | string | Não | Link para publicação original |
| `image_url` | string | Auto | URL assinada da capa (computed) |
| `created_at` | datetime | Auto | Data de criação |
| `updated_at` | datetime | Auto | Data de atualização |
| `autores` | array | Auto | Lista de autores (membros) |
| `subgrupos` | array | Auto | Lista de subgrupos relacionados |

#### Tipos de Publicação (TipoPublicacaoEnum)

| Valor | Descrição |
|-------|-----------|
| `materia` | Matéria/Reportagem |
| `dissertacao` | Dissertação de Mestrado |
| `livro` | Livro |
| `tese` | Tese de Doutorado |
| `capitulo_livro` | Capítulo de Livro |
| `policy_brief` | Policy Brief |
| `Artigo` | Artigo Científico |

#### Schema de Criação (PublicacaoCreate)

```json
{
  "title": "Machine Learning Aplicado à Análise de Políticas Públicas",
  "description": "Este artigo apresenta uma análise utilizando técnicas de ML...",
  "type": "Artigo",
  "year": "2025-03-15",
  "link_externo": "https://doi.org/10.1234/exemplo",
  "autor_ids": [1, 2, 3],
  "subgrupo_ids": [1]
}
```

> **Importante:** Os campos `autor_ids` e `subgrupo_ids` são listas de IDs que estabelecem os relacionamentos Many-to-Many.

#### Schema de Resposta (PublicacaoWithRelations)

```json
{
  "id": 1,
  "title": "Machine Learning Aplicado à Análise de Políticas Públicas",
  "description": "Este artigo apresenta uma análise utilizando técnicas de ML...",
  "type": "Artigo",
  "year": "2025-03-15",
  "link_externo": "https://doi.org/10.1234/exemplo",
  "image_url": "/api/v1/files/publicacoes/images/capa123.jpg?token=xyz&expires=1699999999",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "autores": [
    {"id": 1, "nome": "Dr. João Silva"},
    {"id": 2, "nome": "Dra. Maria Santos"}
  ],
  "subgrupos": [
    {"id": 1, "nome_grupo": "Inteligência Artificial"}
  ]
}
```

---

## Endpoints

### Endpoints de Membros

#### Listar Membros

```http
GET /api/v1/membros/
```

**Query Parameters:**

| Param | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `skip` | int | 0 | Registros a pular |
| `limit` | int | 20 | Máximo de registros |
| `q` | string | - | Termo de busca |
| `subgrupo_id` | int | - | Filtrar por subgrupo |

**Resposta:**
```json
{
  "items": [
    {
      "id": 1,
      "nome": "Dr. João Silva",
      "descricao": "...",
      "email": "joao@email.com",
      "linkedin": "https://...",
      "lattes": "http://...",
      "foto_url": "/api/v1/files/...",
      "bg_url": "/api/v1/files/...",
      "subgrupos": [...],
      "publicacoes": [...]
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 20,
  "has_next": true
}
```

---

#### Obter Membro por ID

```http
GET /api/v1/membros/{id}
```

**Resposta:** `MembroWithRelations`

---

#### Criar Membro

```http
POST /api/v1/membros/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome": "Dr. João Silva",
  "descricao": "Pesquisador",
  "email": "joao@email.com",
  "linkedin": "https://linkedin.com/in/joao",
  "lattes": "http://lattes.cnpq.br/123"
}
```

**Resposta:** `Membro` (201 Created)

---

#### Atualizar Membro

```http
PUT /api/v1/membros/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome": "Dr. João Silva Santos",
  "email": "joao.santos@email.com"
}
```

**Resposta:** `Membro`

---

#### Deletar Membro

```http
DELETE /api/v1/membros/{id}
Authorization: Bearer {token}
```

**Resposta:** 204 No Content

---

#### Upload Foto do Membro

```http
POST /api/v1/membros/{id}/upload-foto
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem]
```

**Resposta:**
```json
{
  "message": "Foto atualizada com sucesso",
  "path": "membros/photos/abc123-uuid.jpg"
}
```

---

#### Upload Background do Membro

```http
POST /api/v1/membros/{id}/upload-background
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem]
```

---

#### Obter Subgrupos de um Membro

```http
GET /api/v1/membros/{id}/subgrupos
```

**Resposta:** `SubgrupoSummary[]`

---

#### Obter Publicações de um Membro

```http
GET /api/v1/membros/{id}/publicacoes
```

**Resposta:** `PublicacaoSummary[]`

---

#### Buscar Membros por Nome

```http
GET /api/v1/membros/search/nome?nome=João
```

---

### Endpoints de Subgrupos

#### Listar Subgrupos

```http
GET /api/v1/subgrupos/
```

**Query Parameters:**

| Param | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `skip` | int | 0 | Registros a pular |
| `limit` | int | 20 | Máximo de registros |
| `q` | string | - | Termo de busca |

---

#### Obter Subgrupo por ID

```http
GET /api/v1/subgrupos/{id}
```

**Resposta:** `SubgrupoWithRelations`

---

#### Criar Subgrupo

```http
POST /api/v1/subgrupos/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nome_grupo": "Inteligência Artificial",
  "descricao": "Pesquisas em IA e ML"
}
```

---

#### Atualizar Subgrupo

```http
PUT /api/v1/subgrupos/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "descricao": "Nova descrição do subgrupo"
}
```

---

#### Deletar Subgrupo

```http
DELETE /api/v1/subgrupos/{id}
Authorization: Bearer {token}
```

---

#### Adicionar Membro ao Subgrupo

```http
POST /api/v1/subgrupos/{id}/membros/{membro_id}
Authorization: Bearer {token}
```

**Resposta:**
```json
{
  "message": "Membro adicionado ao subgrupo com sucesso"
}
```

---

#### Remover Membro do Subgrupo

```http
DELETE /api/v1/subgrupos/{id}/membros/{membro_id}
Authorization: Bearer {token}
```

---

#### Listar Membros do Subgrupo

```http
GET /api/v1/subgrupos/{id}/membros
```

**Resposta:** `MembroSummary[]`

---

#### Upload Ícone do Subgrupo

```http
POST /api/v1/subgrupos/{id}/upload-icone
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem - recomendado SVG ou PNG]
```

---

#### Upload Background do Subgrupo

```http
POST /api/v1/subgrupos/{id}/upload-background
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem]
```

---

#### Upload Infográfico do Subgrupo

```http
POST /api/v1/subgrupos/{id}/upload-infografico
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem]
```

**Resposta:**
```json
{
  "message": "Infográfico adicionado com sucesso",
  "path": "subgrupos/infograficos/uuid.png",
  "total_infograficos": 3
}
```

> **Nota:** Cada subgrupo pode ter múltiplos infográficos. Cada upload adiciona à lista existente.

---

#### Deletar Infográfico do Subgrupo

```http
DELETE /api/v1/subgrupos/{id}/infografico/{index}
Authorization: Bearer {token}
```

> **Nota:** O `index` é a posição do infográfico na lista (0-based).

---

### Endpoints de Publicações

#### Listar Publicações

```http
GET /api/v1/publicacoes/
```

**Query Parameters:**

| Param | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `skip` | int | 0 | Registros a pular |
| `limit` | int | 20 | Máximo de registros |
| `q` | string | - | Termo de busca |
| `tipo` | enum | - | Filtrar por tipo |
| `year` | int | - | Filtrar por ano |
| `autor_id` | int | - | Filtrar por autor |

**Exemplos:**
```http
GET /api/v1/publicacoes/?tipo=Artigo
GET /api/v1/publicacoes/?year=2025
GET /api/v1/publicacoes/?autor_id=1
GET /api/v1/publicacoes/?tipo=Artigo&year=2025
```

---

#### Obter Publicação por ID

```http
GET /api/v1/publicacoes/{id}
```

**Resposta:** `PublicacaoWithRelations`

---

#### Criar Publicação

```http
POST /api/v1/publicacoes/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Título da Publicação",
  "description": "Descrição detalhada",
  "type": "Artigo",
  "year": "2025-03-15",
  "link_externo": "https://doi.org/...",
  "autor_ids": [1, 2],
  "subgrupo_ids": [1]
}
```

> **Importante:** Ao criar uma publicação, você **DEVE** informar os IDs dos autores e subgrupos relacionados.

---

#### Atualizar Publicação

```http
PUT /api/v1/publicacoes/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Novo Título",
  "autor_ids": [1, 2, 3],
  "subgrupo_ids": [1, 2]
}
```

> **Nota:** Ao atualizar `autor_ids` ou `subgrupo_ids`, a lista completa substitui a anterior.

---

#### Deletar Publicação

```http
DELETE /api/v1/publicacoes/{id}
Authorization: Bearer {token}
```

---

#### Upload Imagem da Publicação

```http
POST /api/v1/publicacoes/{id}/upload-image
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [arquivo de imagem - capa da publicação]
```

---

#### Listar Tipos de Publicação

```http
GET /api/v1/publicacoes/tipos/
```

**Resposta:**
```json
["materia", "dissertacao", "livro", "tese", "capitulo_livro", "policy_brief", "Artigo"]
```

---

#### Busca Avançada de Publicações

```http
GET /api/v1/publicacoes/search/avancada?q=machine+learning&tipo=Artigo&year=2025
```

**Resposta:**
```json
{
  "items": [...],
  "total": 10,
  "skip": 0,
  "limit": 20,
  "has_next": false,
  "filters": {
    "query": "machine learning",
    "tipo": "Artigo",
    "year": 2025
  }
}
```

---

#### Estatísticas de Publicações

```http
GET /api/v1/publicacoes/estatisticas/
```

**Resposta:**
```json
{
  "total_publicacoes": 150,
  "por_tipo": {
    "materia": 20,
    "dissertacao": 15,
    "livro": 10,
    "tese": 8,
    "capitulo_livro": 25,
    "policy_brief": 12,
    "Artigo": 60
  },
  "tipos_disponiveis": ["materia", "dissertacao", "livro", "tese", "capitulo_livro", "policy_brief", "Artigo"]
}
```

---

### Endpoints de Arquivos

#### Servir Arquivo

```http
GET /api/v1/files/{path}?token={token}&expires={timestamp}
```

**Parâmetros:**

| Param | Tipo | Descrição |
|-------|------|-----------|
| `path` | string | Caminho do arquivo |
| `token` | string | Token HMAC de assinatura |
| `expires` | string | Timestamp Unix de expiração |

> **Nota:** URLs completas são retornadas automaticamente pelos endpoints da API nos campos `*_url`.

---

### Endpoints de Autenticação

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=senha123
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

#### Verificar Token

```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**Resposta:**
```json
{
  "id": 1,
  "username": "admin",
  "is_active": true
}
```

---

## Paginação

Todos os endpoints de listagem retornam dados paginados.

### Parâmetros

| Param | Tipo | Padrão | Máximo | Descrição |
|-------|------|--------|--------|-----------|
| `skip` | int | 0 | - | Número de registros a pular |
| `limit` | int | 20 | 100 | Número máximo de registros |

### Estrutura de Resposta

```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "has_next": true
}
```

### Exemplo de Paginação no Frontend

```javascript
// Primeira página
const page1 = await fetch('/api/v1/membros/?skip=0&limit=20');

// Segunda página
const page2 = await fetch('/api/v1/membros/?skip=20&limit=20');

// Terceira página
const page3 = await fetch('/api/v1/membros/?skip=40&limit=20');
```

---

## Upload de Imagens

### Formatos Aceitos

| Formato | MIME Type |
|---------|-----------|
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| GIF | `image/gif` |
| WebP | `image/webp` |
| SVG | `image/svg+xml` |

### Exemplo de Upload (JavaScript)

```javascript
async function uploadFoto(membroId, file, token) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`/api/v1/membros/${membroId}/upload-foto`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  return response.json();
}

// Uso com input file
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const result = await uploadFoto(1, file, authToken);
  console.log(result);
});
```

---

## URLs Assinadas

As imagens são protegidas por URLs assinadas com expiração.

### Características

- **Expiração:** 1 hora
- **Assinatura:** HMAC-SHA256
- **Proteção:** Path traversal bloqueado

### Funcionamento

1. A API retorna URLs com `token` e `expires`
2. O frontend usa a URL diretamente
3. Após expiração, deve-se buscar nova URL da API

### Exemplo

```json
{
  "foto_url": "/api/v1/files/membros/photos/abc123.jpg?token=xyz789&expires=1699999999"
}
```

### Renovação de URLs no Frontend

```javascript
// Se a imagem falhar (403), busque novamente os dados
async function loadMembro(id) {
  const response = await fetch(`/api/v1/membros/${id}`);
  const membro = await response.json();

  // A URL retornada sempre é válida por mais 1 hora
  return membro;
}

// Usar em React
function MembroCard({ membroId }) {
  const [membro, setMembro] = useState(null);

  useEffect(() => {
    loadMembro(membroId).then(setMembro);
  }, [membroId]);

  if (!membro) return <Loading />;

  return (
    <div>
      <img
        src={membro.foto_url}
        alt={membro.nome}
        onError={() => loadMembro(membroId).then(setMembro)}
      />
      <h2>{membro.nome}</h2>
    </div>
  );
}
```

---

## Exemplos de Integração Frontend

### React - Listagem de Membros

```jsx
import { useState, useEffect } from 'react';

function MembrosPage() {
  const [membros, setMembros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const limit = 20;

  useEffect(() => {
    fetchMembros();
  }, [page]);

  async function fetchMembros() {
    setLoading(true);
    const response = await fetch(
      `/api/v1/membros/?skip=${page * limit}&limit=${limit}`
    );
    const data = await response.json();
    setMembros(data.items);
    setHasNext(data.has_next);
    setLoading(false);
  }

  return (
    <div>
      <h1>Membros</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <>
          <div className="grid">
            {membros.map(membro => (
              <div key={membro.id} className="card">
                {membro.foto_url && (
                  <img src={membro.foto_url} alt={membro.nome} />
                )}
                <h2>{membro.nome}</h2>
                <p>{membro.descricao}</p>
                {membro.email && <a href={`mailto:${membro.email}`}>{membro.email}</a>}
                {membro.linkedin && <a href={membro.linkedin}>LinkedIn</a>}
                {membro.lattes && <a href={membro.lattes}>Lattes</a>}
                <div>
                  <strong>Subgrupos:</strong>
                  {membro.subgrupos.map(s => s.nome_grupo).join(', ')}
                </div>
              </div>
            ))}
          </div>
          <div className="pagination">
            <button onClick={() => setPage(p => p - 1)} disabled={page === 0}>
              Anterior
            </button>
            <span>Página {page + 1}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={!hasNext}>
              Próxima
            </button>
          </div>
        </>
      )}
    </div>
  );
}
```

### React - Criar Publicação

```jsx
import { useState, useEffect } from 'react';

function CriarPublicacao({ token }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'Artigo',
    year: '',
    link_externo: '',
    autor_ids: [],
    subgrupo_ids: []
  });
  const [membros, setMembros] = useState([]);
  const [subgrupos, setSubgrupos] = useState([]);
  const [tipos, setTipos] = useState([]);

  useEffect(() => {
    // Carregar dados para os selects
    fetch('/api/v1/membros/?limit=100').then(r => r.json()).then(d => setMembros(d.items));
    fetch('/api/v1/subgrupos/?limit=100').then(r => r.json()).then(d => setSubgrupos(d.items));
    fetch('/api/v1/publicacoes/tipos/').then(r => r.json()).then(setTipos);
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    const response = await fetch('/api/v1/publicacoes/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      alert('Publicação criada com sucesso!');
    } else {
      const error = await response.json();
      alert(`Erro: ${error.detail}`);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Título"
        value={formData.title}
        onChange={e => setFormData({...formData, title: e.target.value})}
        required
      />

      <textarea
        placeholder="Descrição"
        value={formData.description}
        onChange={e => setFormData({...formData, description: e.target.value})}
      />

      <select
        value={formData.type}
        onChange={e => setFormData({...formData, type: e.target.value})}
      >
        {tipos.map(tipo => (
          <option key={tipo} value={tipo}>{tipo}</option>
        ))}
      </select>

      <input
        type="date"
        value={formData.year}
        onChange={e => setFormData({...formData, year: e.target.value})}
      />

      <input
        type="url"
        placeholder="Link externo"
        value={formData.link_externo}
        onChange={e => setFormData({...formData, link_externo: e.target.value})}
      />

      {/* Multi-select para autores */}
      <select
        multiple
        value={formData.autor_ids}
        onChange={e => setFormData({
          ...formData,
          autor_ids: [...e.target.selectedOptions].map(o => parseInt(o.value))
        })}
      >
        {membros.map(m => (
          <option key={m.id} value={m.id}>{m.nome}</option>
        ))}
      </select>

      {/* Multi-select para subgrupos */}
      <select
        multiple
        value={formData.subgrupo_ids}
        onChange={e => setFormData({
          ...formData,
          subgrupo_ids: [...e.target.selectedOptions].map(o => parseInt(o.value))
        })}
      >
        {subgrupos.map(s => (
          <option key={s.id} value={s.id}>{s.nome_grupo}</option>
        ))}
      </select>

      <button type="submit">Criar Publicação</button>
    </form>
  );
}
```

### React - Upload de Imagem

```jsx
function UploadImagem({ publicacaoId, token, onSuccess }) {
  const [uploading, setUploading] = useState(false);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        `/api/v1/publicacoes/${publicacaoId}/upload-image`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (response.ok) {
        const result = await response.json();
        onSuccess(result);
      }
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={handleUpload}
        disabled={uploading}
      />
      {uploading && <span>Enviando...</span>}
    </div>
  );
}
```

### API Service (TypeScript)

```typescript
// services/api.ts
const API_BASE = '/api/v1';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_next: boolean;
}

interface Membro {
  id: number;
  nome: string;
  descricao?: string;
  experiencia?: string;
  email?: string;
  linkedin?: string;
  lattes?: string;
  foto_url?: string;
  bg_url?: string;
  created_at: string;
  updated_at: string;
  subgrupos: SubgrupoSummary[];
  publicacoes: PublicacaoSummary[];
}

interface SubgrupoSummary {
  id: number;
  nome_grupo: string;
}

interface PublicacaoSummary {
  id: number;
  title: string;
  type: string;
}

class ApiService {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro na requisição');
    }

    return response.json();
  }

  // Membros
  async getMembros(skip = 0, limit = 20): Promise<PaginatedResponse<Membro>> {
    return this.request(`/membros/?skip=${skip}&limit=${limit}`);
  }

  async getMembro(id: number): Promise<Membro> {
    return this.request(`/membros/${id}`);
  }

  async createMembro(data: Partial<Membro>): Promise<Membro> {
    return this.request('/membros/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateMembro(id: number, data: Partial<Membro>): Promise<Membro> {
    return this.request(`/membros/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteMembro(id: number): Promise<void> {
    await this.request(`/membros/${id}`, { method: 'DELETE' });
  }

  // Upload
  async uploadFotoMembro(id: number, file: File): Promise<{ path: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/membros/${id}/upload-foto`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });

    return response.json();
  }

  // Auth
  async login(username: string, password: string): Promise<{ access_token: string }> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });

    const data = await response.json();
    this.token = data.access_token;
    return data;
  }
}

export const api = new ApiService();
```

---

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição bem sucedida |
| 201 | Created - Recurso criado com sucesso |
| 204 | No Content - Recurso deletado com sucesso |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Token inválido ou ausente |
| 403 | Forbidden - Sem permissão / URL expirada |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Erro de validação |
| 500 | Internal Server Error - Erro interno |

### Formato de Erro

```json
{
  "detail": "Mensagem descritiva do erro"
}
```

### Erros de Validação (422)

```json
{
  "detail": [
    {
      "loc": ["body", "nome"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Considerações para o Frontend Admin

### Fluxo de Criação Recomendado

1. **Criar Membro** → Fazer upload da foto → Associar a subgrupos
2. **Criar Subgrupo** → Fazer upload de ícone/background → Adicionar membros → Adicionar infográficos
3. **Criar Publicação** → Selecionar autores e subgrupos existentes → Fazer upload da capa

### Ordem de Dependência

```
1. Membros (independente)
2. Subgrupos (independente, mas pode ter membros)
3. Publicações (depende de membros e subgrupos existirem)
```

### Cache e Performance

- Cache imagens por até 1 hora (igual ao tempo de expiração)
- Implemente infinite scroll para listas grandes
- Use `has_next` para controlar carregamento
- Pré-carregue próxima página enquanto usuário navega

---

**Versão:** 1.0
**Última atualização:** Dezembro 2025
**Base URL:** `https://seu-dominio.com/api/v1`
