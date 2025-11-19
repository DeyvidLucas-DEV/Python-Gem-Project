from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.models.publicacao import TipoPublicacaoEnum

router = APIRouter()


@router.get("/", response_model=dict)
async def read_publicacoes(
        pagination: deps.PaginationParams = Depends(),
        search: deps.SearchParams = Depends(),
        tipo: Optional[TipoPublicacaoEnum] = Query(None, description="Filtrar por tipo de publicação"),
        year: Optional[int] = Query(None, description="Filtrar por ano"),
        autor_id: Optional[int] = Query(None, description="Filtrar por autor"),
        db: AsyncSession = Depends(deps.get_db_session),
) -> Any:
    """
    Recuperar publicações com paginação e filtros avançados.
    """
    if autor_id:
        publicacoes, total = await crud.publicacao.get_by_autor(
            db,
            autor_id=autor_id,
            skip=pagination.skip,
            limit=pagination.limit
        )
    elif tipo:
        publicacoes, total = await crud.publicacao.get_by_tipo(
            db,
            tipo=tipo,
            skip=pagination.skip,
            limit=pagination.limit
        )
    elif year:
        publicacoes, total = await crud.publicacao.get_by_year(
            db,
            year=year,
            skip=pagination.skip,
            limit=pagination.limit
        )
    elif search.query:
        publicacoes, total = await crud.publicacao.search(
            db,
            query_text=search.query,
            tipo=tipo,
            year=year,
            skip=pagination.skip,
            limit=pagination.limit
        )
    else:
        publicacoes, total = await crud.publicacao.get_multi(
            db,
            skip=pagination.skip,
            limit=pagination.limit,
            load_relations=["autores", "subgrupos"]
        )

    return {
        "items": [schemas.PublicacaoWithRelations.model_validate(pub) for pub in publicacoes],
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_next": (pagination.skip + pagination.limit) < total
    }


@router.post("/", response_model=schemas.PublicacaoWithRelations, status_code=status.HTTP_201_CREATED)
async def create_publicacao(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        publicacao_in: schemas.PublicacaoCreate,
        current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Criar nova publicação com autores e subgrupos.
    Requer autenticação.
    """
    # Validar se autores existem
    for autor_id in publicacao_in.autor_ids:
        autor = await crud.membro.get(db, id=autor_id)
        if not autor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Autor com ID {autor_id} não encontrado"
            )

    # Validar se subgrupos existem
    for subgrupo_id in publicacao_in.subgrupo_ids:
        subgrupo = await crud.subgrupo.get(db, id=subgrupo_id)
        if not subgrupo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subgrupo com ID {subgrupo_id} não encontrado"
            )

    publicacao = await crud.publicacao.create_with_relations(db, obj_in=publicacao_in)

    # Recarregar com relacionamentos
    publicacao_with_relations = await crud.publicacao.get(db, id=publicacao.id, load_relations=["autores", "subgrupos"])
    return schemas.PublicacaoWithRelations.model_validate(publicacao_with_relations)


@router.get("/{id}", response_model=schemas.PublicacaoWithRelations)
async def read_publicacao(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
) -> Any:
    """
    Obter publicação por ID.
    """
    publicacao = await crud.publicacao.get(db, id=id, load_relations=["autores", "subgrupos"])
    if not publicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )
    return schemas.PublicacaoWithRelations.model_validate(publicacao)


@router.put("/{id}", response_model=schemas.PublicacaoWithRelations)
async def update_publicacao(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        publicacao_in: schemas.PublicacaoUpdate,
        current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Atualizar publicação.
    Requer autenticação.
    """
    publicacao = await crud.publicacao.get(db, id=id)
    if not publicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )

    # Validar autores se fornecidos
    if publicacao_in.autor_ids is not None:
        for autor_id in publicacao_in.autor_ids:
            autor = await crud.membro.get(db, id=autor_id)
            if not autor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Autor com ID {autor_id} não encontrado"
                )

    # Validar subgrupos se fornecidos
    if publicacao_in.subgrupo_ids is not None:
        for subgrupo_id in publicacao_in.subgrupo_ids:
            subgrupo = await crud.subgrupo.get(db, id=subgrupo_id)
            if not subgrupo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Subgrupo com ID {subgrupo_id} não encontrado"
                )

    publicacao = await crud.publicacao.update_with_relations(
        db,
        db_obj=publicacao,
        obj_in=publicacao_in
    )

    # Recarregar com relacionamentos
    publicacao_with_relations = await crud.publicacao.get(db, id=publicacao.id, load_relations=["autores", "subgrupos"])
    return schemas.PublicacaoWithRelations.model_validate(publicacao_with_relations)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publicacao(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        current_user: Any = Depends(deps.get_current_active_user),
) -> None:
    """
    Deletar publicação.
    Requer autenticação.
    """
    publicacao = await crud.publicacao.get(db, id=id)
    if not publicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )

    await crud.publicacao.remove(db, id=id)


@router.get("/tipos/", response_model=List[str])
async def get_tipos_publicacao() -> List[str]:
    """
    Obter todos os tipos de publicação disponíveis.
    """
    return [tipo.value for tipo in TipoPublicacaoEnum]


@router.get("/search/avancada", response_model=dict)
async def search_publicacoes_avancada(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        q: str = Query(..., min_length=2, description="Termo de busca"),
        tipo: Optional[TipoPublicacaoEnum] = Query(None, description="Filtrar por tipo"),
        year: Optional[int] = Query(None, description="Filtrar por ano"),
        pagination: deps.PaginationParams = Depends(),
) -> Any:
    """
    Busca avançada em publicações.
    """
    publicacoes, total = await crud.publicacao.search(
        db,
        query_text=q,
        tipo=tipo,
        year=year,
        skip=pagination.skip,
        limit=pagination.limit
    )

    return {
        "items": [schemas.PublicacaoWithRelations.model_validate(pub) for pub in publicacoes],
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_next": (pagination.skip + pagination.limit) < total,
        "filters": {
            "query": q,
            "tipo": tipo.value if tipo else None,
            "year": year
        }
    }


@router.post("/{id}/upload-image")
async def upload_image_publicacao(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
        id: int,
        file: UploadFile = File(...),
        current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Upload da imagem da publicação.
    Requer autenticação.
    """
    publicacao = await crud.publicacao.get(db, id=id)
    if not publicacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação não encontrada"
        )

    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )

    # Ler arquivo
    content = await file.read()

    # Atualizar publicação
    await crud.publicacao.update(
        db,
        db_obj=publicacao,
        obj_in={"image": content}
    )

    return {"message": "Imagem atualizada com sucesso"}


@router.get("/estatisticas/", response_model=dict)
async def get_estatisticas_publicacoes(
        *,
        db: AsyncSession = Depends(deps.get_db_session),
) -> Any:
    """
    Obter estatísticas das publicações.
    """
    # Total de publicações (agora 1 query rápida)
    total = await crud.publicacao.get_count(db)

    # Publicações por tipo (agora 1 query rápida por tipo)
    stats_por_tipo = {}
    for tipo in TipoPublicacaoEnum:
        count = await crud.publicacao.get_count(db, filters={"type": tipo})
        stats_por_tipo[tipo.value] = count

    return {
        "total_publicacoes": total,
        "por_tipo": stats_por_tipo,
        "tipos_disponiveis": [tipo.value for tipo in TipoPublicacaoEnum]
    }