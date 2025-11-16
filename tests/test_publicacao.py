import pytest
import io
from httpx import AsyncClient, ASGITransport
from fastapi import status
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

# Importe seus modelos para criar dados de pré-requisito
# NOTA: Ajuste essas importações para seus modelos reais
from app.models.membro import Membro
from app.models.subgrupo import Subgrupo
from app.models.publicacao import Publicacao, TipoPublicacaoEnum

# Assume que o prefixo /publicacoes é adicionado no app.main
# Se não for, mude os paths (ex: de "/publicacoes/" para "/")
API_PREFIX = "/api/v1/publicacoes"

# Marca todos os testes neste arquivo para usar pytest-asyncio
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def autor_fix(db: AsyncSession) -> Membro:
    """Fixture para criar um Autor (Membro) de teste."""
    # CORREÇÃO: Removido o argumento 'email' que não existe no modelo
    autor = Membro(nome="Autor de Teste", descricao="Um autor para testes")
    db.add(autor)
    await db.commit()
    await db.refresh(autor)
    return autor

@pytest_asyncio.fixture
async def subgrupo_fix(db: AsyncSession) -> Subgrupo:
    """Fixture para criar um Subgrupo de teste."""
    # NOTA: Ajuste os campos conforme seu modelo Subgrupo
    subgrupo = Subgrupo(nome_grupo="Subgrupo de Teste")
    db.add(subgrupo)
    await db.commit()
    await db.refresh(subgrupo)
    return subgrupo


@pytest_asyncio.fixture
async def publicacao_fix(
    db: AsyncSession, autor_fix: Membro, subgrupo_fix: Subgrupo
) -> Publicacao:
    """Fixture para criar uma Publicação de teste."""
    pub = Publicacao(
        title="Publicação de Teste",
        type=TipoPublicacaoEnum.ARTIGO,  # Usar o enum diretamente
        year=date(2025, 1, 1),
        autores=[autor_fix],
        subgrupos=[subgrupo_fix],
    )
    db.add(pub)
    await db.commit()
    await db.refresh(pub)
    return pub


# --- Testes dos Endpoints ---

async def test_create_publicacao(
        client: AsyncClient, db: AsyncSession, autor_fix: Membro, subgrupo_fix: Subgrupo
):
    """Testa POST / (Criar Publicação)"""
    data = {
        "title": "Novo Artigo de Teste",
        "description": "Uma descrição do artigo.",
        "type": "Artigo",  # <-- CORREÇÃO AQUI
        "year": "2025-11-08",
        "autor_ids": [autor_fix.id],
        "subgrupo_ids": [subgrupo_fix.id],
    }
    response = await client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["title"] == data["title"]
    assert result["type"] == data["type"] # <-- Agora vai bater
    assert result["autores"][0]["id"] == autor_fix.id
    assert result["subgrupos"][0]["id"] == subgrupo_fix.id


async def test_create_publicacao_tipo_materia(
        client: AsyncClient, db: AsyncSession, autor_fix: Membro, subgrupo_fix: Subgrupo
):
    """Testa POST / com type='materia' - caso que estava falhando"""
    data = {
        "title": "Matéria de Teste",
        "description": "Uma matéria acadêmica.",
        "type": "materia",  # <-- Teste específico para o valor 'materia'
        "year": "2025-11-16",
        "autor_ids": [autor_fix.id],
        "subgrupo_ids": [subgrupo_fix.id],
    }
    response = await client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["title"] == data["title"]
    assert result["type"] == "materia"
    assert result["autores"][0]["id"] == autor_fix.id
    assert result["subgrupos"][0]["id"] == subgrupo_fix.id


@pytest.mark.parametrize("tipo_enum", [
    "materia",
    "dissertacao",
    "livro",
    "tese",
    "capitulo_livro",
    "policy_brief",
    "Artigo"
])
async def test_create_publicacao_all_enum_types(
        client: AsyncClient, db: AsyncSession, autor_fix: Membro, subgrupo_fix: Subgrupo, tipo_enum: str
):
    """Testa criação de publicação com todos os valores possíveis do enum"""
    data = {
        "title": f"Publicação do tipo {tipo_enum}",
        "description": f"Testando enum {tipo_enum}",
        "type": tipo_enum,
        "year": "2025-01-01",
        "autor_ids": [autor_fix.id],
        "subgrupo_ids": [subgrupo_fix.id],
    }
    response = await client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED, f"Falhou para tipo '{tipo_enum}': {response.text}"

    result = response.json()
    assert result["type"] == tipo_enum


async def test_read_publicacoes_empty(client: AsyncClient):
    """Testa GET / (Listar Publicações - Vazio)"""
    response = await client.get(f"{API_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 0
    assert result["items"] == []


async def test_read_publicacoes_with_data(client: AsyncClient, publicacao_fix: Publicacao):
    """Testa GET / (Listar Publicações - Com Dados)"""
    response = await client.get(f"{API_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 1
    assert result["items"][0]["title"] == publicacao_fix.title


async def test_read_publicacoes_filters(client: AsyncClient, publicacao_fix: Publicacao, autor_fix: Membro):
    """Testa GET / (Filtros de Listagem)"""

    # Filtro por ano
    response_year = await client.get(f"{API_PREFIX}/?year=2025")
    assert response_year.json()["total"] == 1

    response_year_fail = await client.get(f"{API_PREFIX}/?year=2020")
    assert response_year_fail.json()["total"] == 0

    # Filtro por autor
    response_autor = await client.get(f"{API_PREFIX}/?autor_id={autor_fix.id}")
    assert response_autor.json()["total"] == 1


async def test_read_publicacao_by_id(client: AsyncClient, publicacao_fix: Publicacao):
    """Testa GET /{id} (Ler por ID)"""
    response = await client.get(f"{API_PREFIX}/{publicacao_fix.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == publicacao_fix.id
    assert result["title"] == publicacao_fix.title


async def test_read_publicacao_not_found(client: AsyncClient):
    """Testa GET /{id} (ID não encontrado)"""
    response = await client.get(f"{API_PREFIX}/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_publicacao(
        client: AsyncClient, publicacao_fix: Publicacao, autor_fix: Membro
):
    """Testa PUT /{id} (Atualizar Publicação)"""
    new_title = "Título Atualizado"
    data = {
        "title": new_title,
        "autor_ids": [autor_fix.id]  # Precisa reenviar relacionamentos
    }

    response = await client.put(f"{API_PREFIX}/{publicacao_fix.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["title"] == new_title
    assert result["id"] == publicacao_fix.id


async def test_delete_publicacao(client: AsyncClient, db: AsyncSession, publicacao_fix: Publicacao):
    """Testa DELETE /{id} (Deletar Publicação)"""
    # Deleta
    response_del = await client.delete(f"{API_PREFIX}/{publicacao_fix.id}")
    assert response_del.status_code == status.HTTP_204_NO_CONTENT

    # Verifica se foi deletado
    response_get = await client.get(f"{API_PREFIX}/{publicacao_fix.id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND


async def test_get_tipos_publicacao(client: AsyncClient):
    """Testa GET /tipos/"""
    response = await client.get(f"{API_PREFIX}/tipos/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert "materia" in result
    assert "tese" in result


async def test_search_publicacoes_avancada(client: AsyncClient, publicacao_fix: Publicacao):
    """Testa GET /search/avancada"""
    # Busca com sucesso
    response = await client.get(f"{API_PREFIX}/search/avancada?q=Teste")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == publicacao_fix.title

    # Busca sem resultado
    response_fail = await client.get(f"{API_PREFIX}/search/avancada?q=Zebra")
    assert response_fail.json()["total"] == 0


async def test_upload_image_publicacao(client: AsyncClient, publicacao_fix: Publicacao):
    """Testa POST /{id}/upload-image"""
    # Cria um arquivo falso em memória
    fake_image = io.BytesIO(b"fakeimagedata")

    files = {"file": ("test_image.jpg", fake_image, "image/jpeg")}

    response = await client.post(
        f"{API_PREFIX}/{publicacao_fix.id}/upload-image", files=files
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Imagem atualizada com sucesso"}


async def test_get_estatisticas_publicacoes(client: AsyncClient, publicacao_fix: Publicacao):
    """Testa GET /estatisticas/"""
    response = await client.get(f"{API_PREFIX}/estatisticas/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total_publicacoes"] > 0
    assert "por_tipo" in result
    assert "tipos_disponiveis" in result