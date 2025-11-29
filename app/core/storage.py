"""
Módulo de Storage para gerenciamento de arquivos.
Suporta armazenamento local e pode ser estendido para S3/MinIO.
Inclui URLs assinadas com expiração para segurança.
"""
import uuid
import hmac
import hashlib
import time
import re
import aiofiles
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode, parse_qs
from fastapi import UploadFile
from abc import ABC, abstractmethod

from app.core.config import settings

# Tempo de expiração padrão: 1 hora (em segundos)
URL_EXPIRATION_TIME = 3600


class StorageBackend(ABC):
    """Interface abstrata para backends de storage."""

    @abstractmethod
    async def save(self, file: UploadFile, folder: str) -> str:
        """Salva arquivo e retorna o path relativo."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Deleta arquivo pelo path."""
        pass

    @abstractmethod
    def get_url(self, path: str) -> str:
        """Retorna URL pública para o arquivo."""
        pass


class LocalStorage(StorageBackend):
    """
    Backend de storage local (sistema de arquivos).
    Usa o path configurado em UPLOADS_PATH.
    """

    def __init__(self, base_path: Optional[str] = None, base_url: str = "/api/v1/files"):
        self.base_path = Path(base_path or settings.UPLOADS_PATH)
        self.base_url = base_url
        self._ensure_directories()

    def _ensure_directories(self):
        """Cria diretórios necessários se não existirem."""
        folders = ["subgrupos/icons", "subgrupos/backgrounds",
                   "membros/photos", "membros/backgrounds",
                   "publicacoes/images"]
        for folder in folders:
            (self.base_path / folder).mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> str:
        """Gera nome único para o arquivo."""
        ext = Path(original_filename).suffix.lower()
        return f"{uuid.uuid4().hex}{ext}"

    async def save(self, file: UploadFile, folder: str) -> str:
        """
        Salva arquivo no sistema de arquivos local.

        Args:
            file: Arquivo enviado via FastAPI
            folder: Subpasta (ex: "subgrupos/icons")

        Returns:
            Path relativo do arquivo salvo (ex: "subgrupos/icons/abc123.png")
        """
        filename = self._generate_filename(file.filename or "image.png")
        relative_path = f"{folder}/{filename}"
        full_path = self.base_path / relative_path

        # Garante que o diretório existe
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Salva o arquivo de forma assíncrona
        content = await file.read()
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(content)

        # Reset file position caso precise reler
        await file.seek(0)

        return relative_path

    async def delete(self, path: str) -> bool:
        """
        Deleta arquivo do sistema de arquivos.

        Args:
            path: Path relativo do arquivo

        Returns:
            True se deletado com sucesso, False caso contrário
        """
        if not path:
            return False

        full_path = self.base_path / path
        try:
            if full_path.exists():
                full_path.unlink()
                return True
        except Exception:
            pass
        return False

    def get_url(self, path: str) -> str:
        """
        Retorna URL para acessar o arquivo.

        Args:
            path: Path relativo do arquivo

        Returns:
            URL completa para o arquivo
        """
        if not path:
            return ""
        return f"{self.base_url}/{path}"

    def get_full_path(self, path: str) -> Path:
        """Retorna o path completo no sistema de arquivos."""
        return self.base_path / path


# Instância global do storage (pode ser substituída por S3Storage no futuro)
storage = LocalStorage()


def _generate_signature(path: str, expires: int) -> str:
    """
    Gera assinatura HMAC para URL.

    Args:
        path: Caminho do arquivo
        expires: Timestamp de expiração

    Returns:
        Assinatura hexadecimal
    """
    message = f"{path}:{expires}"
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()[:32]  # Usar apenas 32 caracteres
    return signature


def generate_signed_url(path: str, expiration_seconds: int = URL_EXPIRATION_TIME) -> str:
    """
    Gera URL assinada com tempo de expiração.

    Args:
        path: Caminho relativo do arquivo
        expiration_seconds: Tempo de expiração em segundos (padrão: 1 hora)

    Returns:
        URL assinada com token e expiração
    """
    if not path:
        return ""

    expires = int(time.time()) + expiration_seconds
    signature = _generate_signature(path, expires)

    params = urlencode({
        'token': signature,
        'expires': expires
    })

    return f"{storage.base_url}/{path}?{params}"


def verify_signed_url(path: str, token: str, expires: str) -> tuple[bool, str]:
    """
    Verifica se uma URL assinada é válida.

    Args:
        path: Caminho do arquivo
        token: Token de assinatura
        expires: Timestamp de expiração

    Returns:
        Tupla (válido, mensagem de erro)
    """
    try:
        expires_int = int(expires)
    except (ValueError, TypeError):
        return False, "Parâmetro 'expires' inválido"

    # Verificar expiração
    if time.time() > expires_int:
        return False, "URL expirada"

    # Verificar assinatura
    expected_signature = _generate_signature(path, expires_int)
    if not hmac.compare_digest(token, expected_signature):
        return False, "Assinatura inválida"

    return True, ""


def is_safe_path(path: str) -> bool:
    """
    Verifica se o path é seguro (previne path traversal attacks).

    Args:
        path: Caminho a ser verificado

    Returns:
        True se o path é seguro
    """
    # Bloquear path traversal
    if '..' in path or path.startswith('/') or path.startswith('\\'):
        return False

    # Bloquear caracteres perigosos
    if re.search(r'[<>:"|?*\x00-\x1f]', path):
        return False

    # Permitir apenas pastas conhecidas
    allowed_prefixes = ('subgrupos/', 'membros/', 'publicacoes/')
    if not path.startswith(allowed_prefixes):
        return False

    # Permitir apenas extensões de imagem
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')
    if not path.lower().endswith(allowed_extensions):
        return False

    return True


# Funções de conveniência
async def save_file(file: UploadFile, folder: str) -> str:
    """Salva arquivo e retorna path relativo."""
    return await storage.save(file, folder)


async def delete_file(path: str) -> bool:
    """Deleta arquivo pelo path."""
    return await storage.delete(path)


def get_file_url(path: Optional[str]) -> Optional[str]:
    """Retorna URL assinada do arquivo ou None se path for None."""
    if not path:
        return None
    return generate_signed_url(path)
