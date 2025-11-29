from typing import Any, List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.core.config import settings
from app.core.storage import save_file, delete_file

router = APIRouter()


@router.get("/", response_model=dict)
async def read_subgrupos(
        pagination: deps.PaginationParams = Depends(),
        search: deps.SearchParams = Depends(),
        db: AsyncSession = Depends(deps.get_db_session),
) -> Any:
    """
    Recuperar subgrupos com paginação e busca.

    - **skip**: número de registros a pular
    - **limit**: número máximo de registros a retornar
    - **q**: termo de busca (opcional)
    """
    if search.query:
        subgrupos, total = await crud.subgrupo.search(
            db,
            query_text=search.query,
            skip=pagination.skip,
            limit=pagination.limit
        )
    else:
        subgrupos, total = await crud.subgrupo.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            load_relations=["membros", "publicacoes"]
        )

    return {
        "items": [schemas.SubgrupoWithRelations.model_validate(subgrupo) for subgrupo in subgrupos],
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_next": (pagination.skip + pagination.limit) < total
    }


@router.post("/", response_model=schemas.Subgrupo, status_code=status.HTTP_201_CREATED)
async def create_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        subgrupo_in: schemas.SubgrupoCreate,
        current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Criar novo subgrupo.
    Requer autenticação.
    """
    # Verificar se já existe subgrupo com o mesmo nome
    existing = await crud.subgrupo.get_by_nome(db, nome_grupo=subgrupo_in.nome_grupo)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subgrupo com este nome já existe"
        )

    subgrupo = await crud.subgrupo.create(db, obj_in=subgrupo_in)
    return schemas.Subgrupo.model_validate(subgrupo)


@router.get("/{id}", response_model=schemas.SubgrupoWithRelations)
async def read_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> Any:
    """
    Obter subgrupo por ID.
    """
    subgrupo = await crud.subgrupo.get(db, id=id, load_relations=["membros", "publicacoes"])
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )
    return schemas.SubgrupoWithRelations.model_validate(subgrupo)


@router.put("/{id}", response_model=schemas.Subgrupo)
async def update_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        subgrupo_in: schemas.SubgrupoUpdate,
        current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Atualizar subgrupo.
    Requer autenticação.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    # Verificar nome único se estiver sendo alterado
    if subgrupo_in.nome_grupo and subgrupo_in.nome_grupo != subgrupo.nome_grupo:
        existing = await crud.subgrupo.get_by_nome(db, nome_grupo=subgrupo_in.nome_grupo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subgrupo com este nome já existe"
            )

    subgrupo = await crud.subgrupo.update(db, db_obj=subgrupo, obj_in=subgrupo_in)
    return schemas.Subgrupo.model_validate(subgrupo)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        current_user: Any = Depends(deps.get_current_active_user),
) -> None:
    """
    Deletar subgrupo.
    Requer autenticação.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    await crud.subgrupo.remove(db, id=id)


@router.post("/{id}/membros/{membro_id}", status_code=status.HTTP_201_CREATED)
async def add_membro_to_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        membro_id: int,
        current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Adicionar membro ao subgrupo.
    Requer autenticação.
    """
    # Verificar se subgrupo existe
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    # Verificar se membro existe
    membro = await crud.membro.get(db, id=membro_id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    # Adicionar associação
    success = await crud.subgrupo.add_membro(db, subgrupo_id=id, membro_id=membro_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Membro já está associado a este subgrupo"
        )

    return {"message": "Membro adicionado ao subgrupo com sucesso"}


@router.delete("/{id}/membros/{membro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_membro_from_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        membro_id: int,
        current_user: Any = Depends(deps.get_current_active_user),
) -> None:
    """
    Remover membro do subgrupo.
    Requer autenticação.
    """
    success = await crud.subgrupo.remove_membro(db, subgrupo_id=id, membro_id=membro_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associação não encontrada"
        )


@router.get("/{id}/membros", response_model=List[schemas.MembroSummary])
async def get_subgrupo_membros(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> Any:
    """
    Obter todos os membros de um subgrupo.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    membros = await crud.subgrupo.get_membros(db, subgrupo_id=id)
    return [schemas.MembroSummary.model_validate(membro) for membro in membros]


@router.post("/{id}/upload-icone")
async def upload_icone_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        file: UploadFile = File(...),
        current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Upload do ícone do subgrupo.
    Requer autenticação.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )

    # Deletar arquivo antigo se existir
    if subgrupo.icone_grupo_path:
        await delete_file(subgrupo.icone_grupo_path)

    # Salvar novo arquivo
    file_path = await save_file(file, "subgrupos/icons")

    # Atualizar subgrupo com o path do arquivo
    await crud.subgrupo.update(
        db,
        db_obj=subgrupo,
        obj_in={"icone_grupo_path": file_path}
    )

    return {"message": "Ícone atualizado com sucesso", "path": file_path}


@router.post("/{id}/upload-background")
async def upload_background_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        file: UploadFile = File(...),
        current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Upload do background do subgrupo.
    Requer autenticação.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )

    # Deletar arquivo antigo se existir
    if subgrupo.bg_path:
        await delete_file(subgrupo.bg_path)

    # Salvar novo arquivo
    file_path = await save_file(file, "subgrupos/backgrounds")

    # Atualizar subgrupo com o path do arquivo
    await crud.subgrupo.update(
        db,
        db_obj=subgrupo,
        obj_in={"bg_path": file_path}
    )

    return {"message": "Background atualizado com sucesso", "path": file_path}


@router.post("/{id}/upload-infografico")
async def upload_infografico_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        file: UploadFile = File(...),
        current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Upload de um infográfico do subgrupo.
    Adiciona à lista de infográficos existentes.
    Requer autenticação.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )

    # Salvar novo arquivo
    file_path = await save_file(file, "subgrupos/infograficos")

    # Obter lista atual de infográficos
    current_infograficos = []
    if subgrupo.infograficos:
        try:
            current_infograficos = json.loads(subgrupo.infograficos)
        except (json.JSONDecodeError, TypeError):
            current_infograficos = []

    # Adicionar novo path
    current_infograficos.append(file_path)

    # Atualizar subgrupo
    await crud.subgrupo.update(
        db,
        db_obj=subgrupo,
        obj_in={"infograficos": json.dumps(current_infograficos)}
    )

    return {
        "message": "Infográfico adicionado com sucesso",
        "path": file_path,
        "total_infograficos": len(current_infograficos)
    }


@router.delete("/{id}/infografico/{index}")
async def delete_infografico_subgrupo(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        index: int,
        current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Remove um infográfico do subgrupo pelo índice.
    Requer autenticação.
    """
    subgrupo = await crud.subgrupo.get(db, id=id)
    if not subgrupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subgrupo não encontrado"
        )

    # Obter lista atual de infográficos
    current_infograficos = []
    if subgrupo.infograficos:
        try:
            current_infograficos = json.loads(subgrupo.infograficos)
        except (json.JSONDecodeError, TypeError):
            current_infograficos = []

    if index < 0 or index >= len(current_infograficos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Índice inválido. Total de infográficos: {len(current_infograficos)}"
        )

    # Deletar arquivo
    file_path = current_infograficos[index]
    await delete_file(file_path)

    # Remover da lista
    current_infograficos.pop(index)

    # Atualizar subgrupo
    await crud.subgrupo.update(
        db,
        db_obj=subgrupo,
        obj_in={"infograficos": json.dumps(current_infograficos) if current_infograficos else None}
    )

    return {
        "message": "Infográfico removido com sucesso",
        "total_infograficos": len(current_infograficos)
    }