"""
Endpoint para servir arquivos estáticos (imagens) com URLs assinadas.
Requer token válido e não expirado para acessar os arquivos.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import FileResponse

from app.core.storage import storage, verify_signed_url, is_safe_path

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{file_path:path}")
async def serve_file(
    file_path: str,
    token: str = Query(..., description="Token de assinatura"),
    expires: str = Query(..., description="Timestamp de expiração")
):
    """
    Serve arquivos estáticos (imagens) com verificação de URL assinada.

    Requer parâmetros 'token' e 'expires' válidos na query string.
    URLs expiradas ou com assinatura inválida serão rejeitadas.

    Args:
        file_path: Caminho relativo do arquivo
        token: Token HMAC de assinatura
        expires: Timestamp Unix de expiração

    Returns:
        FileResponse com o arquivo solicitado
    """
    # 1. Validar segurança do path (previne path traversal)
    if not is_safe_path(file_path):
        logger.warning(f"Tentativa de acesso a path inseguro: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    # 2. Verificar URL assinada
    is_valid, error_message = verify_signed_url(file_path, token, expires)
    if not is_valid:
        logger.warning(f"URL inválida para {file_path}: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message
        )

    # 3. Verificar se arquivo existe
    full_path = storage.get_full_path(file_path)

    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )

    # 4. Verificar se está dentro do diretório permitido
    try:
        full_path.resolve().relative_to(storage.base_path.resolve())
    except ValueError:
        logger.warning(f"Tentativa de path traversal: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    # 5. Determinar content-type
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

    # 6. Retornar arquivo com cache curto (já que URL expira)
    return FileResponse(
        path=full_path,
        media_type=media_type,
        headers={
            "Cache-Control": "private, max-age=3600",  # Cache de 1 hora (igual à expiração)
            "X-Content-Type-Options": "nosniff",  # Previne MIME sniffing
        }
    )
