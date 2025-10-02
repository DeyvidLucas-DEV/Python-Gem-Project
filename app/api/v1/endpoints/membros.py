from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=dict)
async def read_membros(
        pagination: deps.PaginationParams = Depends(),
        search: deps.SearchParams = Depends(),
        subgrupo_id: Optional[int] = Query(None, description="Filtrar por subgrupo"),
        db: AsyncSession = Depends(deps.get_db_session),
) -> Any:
    """
    Recuperar membros com paginação e filtros.
    """
    if subgrupo_id:
        membros, total = await crud.membro.get_by_subgrupo(
            db,
            subgrupo_id=subgrupo_id,
            skip=pagination.skip,
            limit=pagination.limit
        )
    elif search.query:
        membros, total = await crud.membro.search(
            db,
            query_text=search.query,
            skip=pagination.skip,
            limit=pagination.limit
        )
    else:
        membros, total = await crud.membro.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            load_relations=True
        )

    return {
        "items": [schemas.MembroWithRelations.model_validate(membro) for membro in membros],
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_next": (pagination.skip + pagination.limit) < total
    }


@router.post("/", response_model=schemas.Membro, status_code=status.HTTP_201_CREATED)
async def create_membro(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        membro_in: schemas.MembroCreate,
) -> Any:
    """
    Criar novo membro.
    """
    membro = await crud.membro.create(db, obj_in=membro_in)
    return schemas.Membro.model_validate(membro)


@router.get("/{id}", response_model=schemas.MembroWithRelations)
async def read_membro(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> Any:
    """
    Obter membro por ID.
    """
    membro = await crud.membro.get(db, id=id, load_relations=True)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )
    return schemas.MembroWithRelations.model_validate(membro)


@router.put("/{id}", response_model=schemas.Membro)
async def update_membro(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        membro_in: schemas.MembroUpdate,
) -> Any:
    """
    Atualizar membro.
    """
    membro = await crud.membro.get(db, id=id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    membro = await crud.membro.update(db, db_obj=membro, obj_in=membro_in)
    return schemas.Membro.model_validate(membro)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_membro(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> None:
    """
    Deletar membro.
    """
    membro = await crud.membro.get(db, id=id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    await crud.membro.remove(db, id=id)


@router.get("/{id}/subgrupos", response_model=List[schemas.SubgrupoSummary])
async def get_membro_subgrupos(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> Any:
    """
    Obter todos os subgrupos de um membro.
    """
    membro = await crud.membro.get(db, id=id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    subgrupos = await crud.membro.get_subgrupos(db, membro_id=id)
    return [schemas.SubgrupoSummary.model_validate(subgrupo) for subgrupo in subgrupos]


@router.get("/{id}/publicacoes", response_model=List[schemas.PublicacaoSummary])
async def get_membro_publicacoes(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> Any:
    """
    Obter todas as publicações de um membro.
    """
    membro = await crud.membro.get(db, id=id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    publicacoes = await crud.membro.get_publicacoes(db, membro_id=id)
    return [schemas.PublicacaoSummary.model_validate(pub) for pub in publicacoes]


@router.post("/{id}/upload-foto")
async def upload_foto_membro(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        file: UploadFile = File(...),
) -> dict:
    """
    Upload da foto do membro.
    """
    membro = await crud.membro.get(db, id=id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )

    # Ler arquivo
    content = await file.read()

    # Atualizar membro
    await crud.membro.update(
        db,
        db_obj=membro,
        obj_in={"foto": content}
    )

    return {"message": "Foto atualizada com sucesso"}


@router.post("/{id}/upload-background")
async def upload_background_membro(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        file: UploadFile = File(...),
) -> dict:
    """
    Upload do background do membro.
    """
    membro = await crud.membro.get(db, id=id)
    if not membro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membro não encontrado"
        )

    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )

    # Ler arquivo
    content = await file.read()

    # Atualizar membro
    await crud.membro.update(
        db,
        db_obj=membro,
        obj_in={"bg": content}
    )

    return {"message": "Background atualizado com sucesso"}


@router.get("/search/nome", response_model=dict)
async def search_membros_by_nome(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        nome: str = Query(..., min_length=2, description="Nome ou parte do nome para buscar"),
        pagination: deps.PaginationParams = Depends(),
) -> Any:
    """
    Buscar membros por nome.
    """
    membros, total = await crud.membro.search_by_nome(
        db,
        nome_partial=nome,
        skip=pagination.skip,
        limit=pagination.limit
    )

    return {
        "items": [schemas.MembroWithRelations.model_validate(membro) for membro in membros],
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_next": (pagination.skip + pagination.limit) < total
    }