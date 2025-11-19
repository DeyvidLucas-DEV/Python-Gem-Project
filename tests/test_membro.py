import pytest
import io
from httpx import AsyncClient
from fastapi import status
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membro import Membro
from app.models.subgrupo import Subgrupo
from app.models.publicacao import Publicacao, TipoPublicacaoEnum
from datetime import date

API_PREFIX = "/api/v1/membros"

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def membro_fix(db: AsyncSession) -> Membro:
    """Fixture para criar um Membro de teste."""
    membro = Membro(nome="João da Silva", descricao="Pesquisador sênior")
    db.add(membro)
    await db.commit()
    await db.refresh(membro)
    return membro


@pytest_asyncio.fixture
async def subgrupo_fix(db: AsyncSession) -> Subgrupo:
    """Fixture para criar um Subgrupo de teste."""
    subgrupo = Subgrupo(nome_grupo="Subgrupo Teste")
    db.add(subgrupo)
    await db.commit()
    await db.refresh(subgrupo)
    return subgrupo


@pytest_asyncio.fixture
async def membro_com_relacoes_fix(
    db: AsyncSession, membro_fix: Membro, subgrupo_fix: Subgrupo
) -> Membro:
    """Fixture para criar um Membro com subgrupos e publicações."""
    # Adicionar subgrupo ao membro
    membro_fix.subgrupos.append(subgrupo_fix)

    # Criar publicação
    pub = Publicacao(
        title="Publicação do Membro",
        type=TipoPublicacaoEnum.ARTIGO,
        year=date(2025, 1, 1),
        autores=[membro_fix],
        subgrupos=[subgrupo_fix],
    )
    db.add(pub)
    await db.commit()
    await db.refresh(membro_fix)
    return membro_fix


# --- Testes dos Endpoints ---

async def test_read_membros_empty(client: AsyncClient):
    """Testa GET / (Listar Membros - Vazio)"""
    response = await client.get(f"{API_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 0
    assert result["items"] == []


async def test_read_membros_with_data(client: AsyncClient, membro_fix: Membro):
    """Testa GET / (Listar Membros - Com Dados)"""
    response = await client.get(f"{API_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 1
    assert result["items"][0]["nome"] == membro_fix.nome


async def test_read_membros_pagination(client: AsyncClient, db: AsyncSession):
    """Testa GET / (Paginação)"""
    # Criar vários membros
    for i in range(5):
        membro = Membro(nome=f"Membro {i}")
        db.add(membro)
    await db.commit()

    # Testar paginação
    response = await client.get(f"{API_PREFIX}/?skip=0&limit=2")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result["items"]) == 2
    assert result["total"] == 5
    assert result["has_next"] is True


async def test_create_membro(auth_client: AsyncClient):
    """Testa POST / (Criar Membro)"""
    data = {
        "nome": "Maria Santos"
    }
    response = await auth_client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["nome"] == data["nome"]
    assert "id" in result


async def test_create_membro_with_description(auth_client: AsyncClient):
    """Testa POST / (Criar Membro com descrição)"""
    data = {
        "nome": "Pedro Oliveira",
        "descricao": "Pesquisador júnior"
    }
    response = await auth_client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["nome"] == data["nome"]


async def test_read_membro_by_id(client: AsyncClient, membro_fix: Membro):
    """Testa GET /{id} (Ler por ID)"""
    response = await client.get(f"{API_PREFIX}/{membro_fix.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == membro_fix.id
    assert result["nome"] == membro_fix.nome


async def test_read_membro_not_found(client: AsyncClient):
    """Testa GET /{id} (ID não encontrado)"""
    response = await client.get(f"{API_PREFIX}/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_membro(auth_client: AsyncClient, membro_fix: Membro):
    """Testa PUT /{id} (Atualizar Membro)"""
    new_nome = "João Silva Atualizado"
    data = {
        "nome": new_nome,
        "descricao": "Descrição atualizada"
    }

    response = await auth_client.put(f"{API_PREFIX}/{membro_fix.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["nome"] == new_nome
    assert result["id"] == membro_fix.id


async def test_update_membro_partial(auth_client: AsyncClient, membro_fix: Membro):
    """Testa PUT /{id} (Atualização parcial)"""
    data = {
        "nome": "Novo Nome"
    }

    response = await auth_client.put(f"{API_PREFIX}/{membro_fix.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["nome"] == "Novo Nome"
    # Descrição deve permanecer a mesma
    assert result["descricao"] == membro_fix.descricao


async def test_delete_membro(auth_client: AsyncClient, db: AsyncSession, membro_fix: Membro):
    """Testa DELETE /{id} (Deletar Membro)"""
    # Deleta
    response_del = await auth_client.delete(f"{API_PREFIX}/{membro_fix.id}")
    assert response_del.status_code == status.HTTP_204_NO_CONTENT

    # Verifica se foi deletado
    response_get = await auth_client.get(f"{API_PREFIX}/{membro_fix.id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND


async def test_get_membro_subgrupos(
    client: AsyncClient, membro_com_relacoes_fix: Membro, subgrupo_fix: Subgrupo
):
    """Testa GET /{id}/subgrupos"""
    response = await client.get(f"{API_PREFIX}/{membro_com_relacoes_fix.id}/subgrupos")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) >= 1
    assert result[0]["id"] == subgrupo_fix.id
    assert result[0]["nome_grupo"] == subgrupo_fix.nome_grupo


async def test_get_membro_publicacoes(
    client: AsyncClient, membro_com_relacoes_fix: Membro
):
    """Testa GET /{id}/publicacoes"""
    response = await client.get(f"{API_PREFIX}/{membro_com_relacoes_fix.id}/publicacoes")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) >= 1
    assert result[0]["title"] == "Publicação do Membro"


async def test_upload_foto_membro(auth_client: AsyncClient, membro_fix: Membro):
    """Testa POST /{id}/upload-foto"""
    # Cria um arquivo falso em memória
    fake_image = io.BytesIO(b"fakeimagedatafortest")

    files = {"file": ("foto.jpg", fake_image, "image/jpeg")}

    response = await auth_client.post(
        f"{API_PREFIX}/{membro_fix.id}/upload-foto", files=files
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Foto atualizada com sucesso"}


async def test_upload_foto_invalid_type(auth_client: AsyncClient, membro_fix: Membro):
    """Testa POST /{id}/upload-foto com tipo de arquivo inválido"""
    fake_file = io.BytesIO(b"notanimagefile")

    files = {"file": ("document.pdf", fake_file, "application/pdf")}

    response = await auth_client.post(
        f"{API_PREFIX}/{membro_fix.id}/upload-foto", files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_upload_background_membro(auth_client: AsyncClient, membro_fix: Membro):
    """Testa POST /{id}/upload-background"""
    fake_image = io.BytesIO(b"fakebackgrounddata")

    files = {"file": ("background.jpg", fake_image, "image/jpeg")}

    response = await auth_client.post(
        f"{API_PREFIX}/{membro_fix.id}/upload-background", files=files
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Background atualizado com sucesso"}


async def test_search_membros_by_nome(client: AsyncClient, db: AsyncSession):
    """Testa GET /search/nome"""
    # Criar alguns membros com nomes diferentes
    membro1 = Membro(nome="Carlos Alberto")
    membro2 = Membro(nome="Carlos Silva")
    membro3 = Membro(nome="Ana Maria")
    db.add_all([membro1, membro2, membro3])
    await db.commit()

    # Busca por "Carlos"
    response = await client.get(f"{API_PREFIX}/search/nome?nome=Carlos")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 2
    assert all("Carlos" in item["nome"] for item in result["items"])


async def test_search_membros_by_nome_no_results(client: AsyncClient):
    """Testa GET /search/nome sem resultados"""
    response = await client.get(f"{API_PREFIX}/search/nome?nome=NomeInexistente")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 0
    assert result["items"] == []


async def test_read_membros_with_subgrupo_filter(
    client: AsyncClient, membro_com_relacoes_fix: Membro, subgrupo_fix: Subgrupo
):
    """Testa GET / com filtro de subgrupo"""
    response = await client.get(f"{API_PREFIX}/?subgrupo_id={subgrupo_fix.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] >= 1
    assert any(item["id"] == membro_com_relacoes_fix.id for item in result["items"])


async def test_read_membros_with_search_query(
    client: AsyncClient, membro_fix: Membro
):
    """Testa GET / com query de busca"""
    response = await client.get(f"{API_PREFIX}/?q={membro_fix.nome[:5]}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] >= 1
