from fastapi import APIRouter

from app.api.v1.endpoints import subgrupos, membros, publicacoes, auth, files

api_router = APIRouter()

# Rotas de autenticação (sem prefixo adicional)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["autenticação"]
)

# Rotas para servir arquivos estáticos (imagens)
api_router.include_router(
    files.router,
    prefix="/files",
    tags=["arquivos"]
)

api_router.include_router(
    subgrupos.router,
    prefix="/subgrupos",
    tags=["subgrupos"]
)

api_router.include_router(
    membros.router,
    prefix="/membros",
    tags=["membros"]
)

api_router.include_router(
    publicacoes.router,
    prefix="/publicacoes",
    tags=["publicações"]
)