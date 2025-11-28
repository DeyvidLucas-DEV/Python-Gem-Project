"""
Módulo de Storage para gerenciamento de arquivos.
Suporta armazenamento local e pode ser estendido para S3/MinIO.
"""
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from abc import ABC, abstractmethod

from app.core.config import settings


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


# Funções de conveniência
async def save_file(file: UploadFile, folder: str) -> str:
    """Salva arquivo e retorna path relativo."""
    return await storage.save(file, folder)


async def delete_file(path: str) -> bool:
    """Deleta arquivo pelo path."""
    return await storage.delete(path)


def get_file_url(path: Optional[str]) -> Optional[str]:
    """Retorna URL do arquivo ou None se path for None."""
    if not path:
        return None
    return storage.get_url(path)
