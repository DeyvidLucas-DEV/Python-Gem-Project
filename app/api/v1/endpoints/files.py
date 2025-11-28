"""
Endpoint para servir arquivos estáticos (imagens).
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.core.storage import storage

router = APIRouter()


@router.get("/{file_path:path}")
async def serve_file(file_path: str):
    """
    Serve arquivos estáticos (imagens) armazenados localmente.

    Args:
        file_path: Caminho relativo do arquivo (ex: subgrupos/icons/abc123.png)

    Returns:
        FileResponse com o arquivo solicitado
    """
    full_path = storage.get_full_path(file_path)

    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )

    # Verificar se está dentro do diretório permitido (segurança)
    try:
        full_path.resolve().relative_to(storage.base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    # Determinar content-type baseado na extensão
    suffix = full_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }
    media_type = media_types.get(suffix, "application/octet-stream")

    return FileResponse(
        path=full_path,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=31536000",  # Cache por 1 ano
        }
    )
