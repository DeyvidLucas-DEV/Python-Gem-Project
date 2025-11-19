import pytest
import io
from httpx import AsyncClient
from fastapi import status
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subgrupo import Subgrupo
from app.models.membro import Membro

API_PREFIX = "/api/v1/subgrupos"

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def subgrupo_fix(db: AsyncSession) -> Subgrupo:
    """Fixture para criar um Subgrupo de teste."""
    subgrupo = Subgrupo(
        nome_grupo="Grupo de Pesquisa",
        descricao="Um grupo de pesquisa em computação"
    )
    db.add(subgrupo)
    await db.commit()
    await db.refresh(subgrupo)
    return subgrupo


@pytest_asyncio.fixture
async def membro_fix(db: AsyncSession) -> Membro:
    """Fixture para criar um Membro de teste."""
    membro = Membro(nome="João Silva", descricao="Pesquisador")
    db.add(membro)
    await db.commit()
    await db.refresh(membro)
    return membro


@pytest_asyncio.fixture
async def subgrupo_com_membros_fix(
    db: AsyncSession, subgrupo_fix: Subgrupo, membro_fix: Membro
) -> Subgrupo:
    """Fixture para criar um Subgrupo com membros."""
    subgrupo_fix.membros.append(membro_fix)
    await db.commit()
    await db.refresh(subgrupo_fix)
    return subgrupo_fix


# --- Testes dos Endpoints ---

async def test_read_subgrupos_empty(client: AsyncClient):
    """Testa GET / (Listar Subgrupos - Vazio)"""
    response = await client.get(f"{API_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 0
    assert result["items"] == []


async def test_read_subgrupos_with_data(client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa GET / (Listar Subgrupos - Com Dados)"""
    response = await client.get(f"{API_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 1
    assert result["items"][0]["nome_grupo"] == subgrupo_fix.nome_grupo
    assert result["items"][0]["descricao"] == subgrupo_fix.descricao


async def test_read_subgrupos_pagination(client: AsyncClient, db: AsyncSession):
    """Testa GET / (Paginação)"""
    # Criar vários subgrupos
    for i in range(5):
        subgrupo = Subgrupo(nome_grupo=f"Grupo {i}")
        db.add(subgrupo)
    await db.commit()

    # Testar paginação
    response = await client.get(f"{API_PREFIX}/?skip=0&limit=2")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result["items"]) == 2
    assert result["total"] == 5
    assert result["has_next"] is True


async def test_create_subgrupo(auth_client: AsyncClient):
    """Testa POST / (Criar Subgrupo)"""
    data = {
        "nome_grupo": "Novo Grupo",
        "descricao": "Descrição do novo grupo"
    }
    response = await auth_client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["nome_grupo"] == data["nome_grupo"]
    assert result["descricao"] == data["descricao"]
    assert "id" in result


async def test_create_subgrupo_without_description(auth_client: AsyncClient):
    """Testa POST / (Criar Subgrupo sem descrição)"""
    data = {
        "nome_grupo": "Grupo Sem Descrição"
    }
    response = await auth_client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert result["nome_grupo"] == data["nome_grupo"]


async def test_create_subgrupo_duplicate_name(
    auth_client: AsyncClient, subgrupo_fix: Subgrupo
):
    """Testa POST / (Criar Subgrupo com nome duplicado)"""
    data = {
        "nome_grupo": subgrupo_fix.nome_grupo,
        "descricao": "Tentando criar duplicado"
    }
    response = await auth_client.post(f"{API_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já existe" in response.json()["detail"].lower()


async def test_read_subgrupo_by_id(client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa GET /{id} (Ler por ID)"""
    response = await client.get(f"{API_PREFIX}/{subgrupo_fix.id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == subgrupo_fix.id
    assert result["nome_grupo"] == subgrupo_fix.nome_grupo
    assert result["descricao"] == subgrupo_fix.descricao


async def test_read_subgrupo_not_found(client: AsyncClient):
    """Testa GET /{id} (ID não encontrado)"""
    response = await client.get(f"{API_PREFIX}/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_subgrupo(auth_client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa PUT /{id} (Atualizar Subgrupo)"""
    new_nome = "Grupo Atualizado"
    data = {
        "nome_grupo": new_nome,
        "descricao": "Nova descrição"
    }

    response = await auth_client.put(f"{API_PREFIX}/{subgrupo_fix.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["nome_grupo"] == new_nome
    assert result["descricao"] == data["descricao"]
    assert result["id"] == subgrupo_fix.id


async def test_update_subgrupo_partial(auth_client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa PUT /{id} (Atualização parcial)"""
    data = {
        "nome_grupo": "Novo Nome Apenas"
    }

    response = await auth_client.put(f"{API_PREFIX}/{subgrupo_fix.id}", json=data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["nome_grupo"] == "Novo Nome Apenas"
    # Descrição deve permanecer a mesma
    assert result["descricao"] == subgrupo_fix.descricao


async def test_update_subgrupo_duplicate_name(
    auth_client: AsyncClient, db: AsyncSession, subgrupo_fix: Subgrupo
):
    """Testa PUT /{id} (Atualizar com nome duplicado)"""
    # Criar outro subgrupo
    outro_subgrupo = Subgrupo(nome_grupo="Outro Grupo")
    db.add(outro_subgrupo)
    await db.commit()
    await db.refresh(outro_subgrupo)

    # Tentar atualizar para o mesmo nome
    data = {
        "nome_grupo": subgrupo_fix.nome_grupo
    }

    response = await auth_client.put(f"{API_PREFIX}/{outro_subgrupo.id}", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já existe" in response.json()["detail"].lower()


async def test_delete_subgrupo(
    auth_client: AsyncClient, db: AsyncSession, subgrupo_fix: Subgrupo
):
    """Testa DELETE /{id} (Deletar Subgrupo)"""
    # Deleta
    response_del = await auth_client.delete(f"{API_PREFIX}/{subgrupo_fix.id}")
    assert response_del.status_code == status.HTTP_204_NO_CONTENT

    # Verifica se foi deletado
    response_get = await auth_client.get(f"{API_PREFIX}/{subgrupo_fix.id}")
    assert response_get.status_code == status.HTTP_404_NOT_FOUND


async def test_add_membro_to_subgrupo(
    auth_client: AsyncClient, subgrupo_fix: Subgrupo, membro_fix: Membro
):
    """Testa POST /{id}/membros/{membro_id} (Adicionar membro)"""
    response = await auth_client.post(
        f"{API_PREFIX}/{subgrupo_fix.id}/membros/{membro_fix.id}"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Membro adicionado ao subgrupo com sucesso"


async def test_add_membro_already_in_subgrupo(
    auth_client: AsyncClient, subgrupo_com_membros_fix: Subgrupo, membro_fix: Membro
):
    """Testa POST /{id}/membros/{membro_id} (Membro já associado)"""
    response = await auth_client.post(
        f"{API_PREFIX}/{subgrupo_com_membros_fix.id}/membros/{membro_fix.id}"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já está associado" in response.json()["detail"].lower()


async def test_add_membro_subgrupo_not_found(auth_client: AsyncClient, membro_fix: Membro):
    """Testa POST /{id}/membros/{membro_id} (Subgrupo não encontrado)"""
    response = await auth_client.post(f"{API_PREFIX}/9999/membros/{membro_fix.id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_add_membro_not_found_to_subgrupo(
    auth_client: AsyncClient, subgrupo_fix: Subgrupo
):
    """Testa POST /{id}/membros/{membro_id} (Membro não encontrado)"""
    response = await auth_client.post(f"{API_PREFIX}/{subgrupo_fix.id}/membros/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_remove_membro_from_subgrupo(
    auth_client: AsyncClient, subgrupo_com_membros_fix: Subgrupo, membro_fix: Membro
):
    """Testa DELETE /{id}/membros/{membro_id} (Remover membro)"""
    response = await auth_client.delete(
        f"{API_PREFIX}/{subgrupo_com_membros_fix.id}/membros/{membro_fix.id}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_remove_membro_not_associated(
    auth_client: AsyncClient, subgrupo_fix: Subgrupo, membro_fix: Membro
):
    """Testa DELETE /{id}/membros/{membro_id} (Associação não existe)"""
    response = await auth_client.delete(
        f"{API_PREFIX}/{subgrupo_fix.id}/membros/{membro_fix.id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_subgrupo_membros(
    client: AsyncClient, subgrupo_com_membros_fix: Subgrupo, membro_fix: Membro
):
    """Testa GET /{id}/membros"""
    response = await client.get(f"{API_PREFIX}/{subgrupo_com_membros_fix.id}/membros")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) >= 1
    assert result[0]["id"] == membro_fix.id
    assert result[0]["nome"] == membro_fix.nome


async def test_get_subgrupo_membros_empty(client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa GET /{id}/membros (Vazio)"""
    response = await client.get(f"{API_PREFIX}/{subgrupo_fix.id}/membros")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result) == 0


async def test_upload_icone_subgrupo(auth_client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa POST /{id}/upload-icone"""
    fake_image = io.BytesIO(b"fakeiconedata")

    files = {"file": ("icone.png", fake_image, "image/png")}

    response = await auth_client.post(
        f"{API_PREFIX}/{subgrupo_fix.id}/upload-icone", files=files
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Ícone atualizado com sucesso"}


async def test_upload_icone_invalid_type(auth_client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa POST /{id}/upload-icone com tipo de arquivo inválido"""
    fake_file = io.BytesIO(b"notanimagefile")

    files = {"file": ("document.txt", fake_file, "text/plain")}

    response = await auth_client.post(
        f"{API_PREFIX}/{subgrupo_fix.id}/upload-icone", files=files
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_upload_background_subgrupo(auth_client: AsyncClient, subgrupo_fix: Subgrupo):
    """Testa POST /{id}/upload-background"""
    fake_image = io.BytesIO(b"fakebackgrounddata")

    files = {"file": ("background.jpg", fake_image, "image/jpeg")}

    response = await auth_client.post(
        f"{API_PREFIX}/{subgrupo_fix.id}/upload-background", files=files
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Background atualizado com sucesso"}


async def test_read_subgrupos_with_search_query(
    client: AsyncClient, subgrupo_fix: Subgrupo
):
    """Testa GET / com query de busca"""
    response = await client.get(f"{API_PREFIX}/?q={subgrupo_fix.nome_grupo[:5]}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] >= 1


async def test_read_subgrupos_with_search_query_no_results(client: AsyncClient):
    """Testa GET / com query de busca sem resultados"""
    response = await client.get(f"{API_PREFIX}/?q=NomeInexistente123")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["total"] == 0
