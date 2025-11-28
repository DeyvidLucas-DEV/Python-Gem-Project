"""Migrate images from LargeBinary to file storage paths

Revision ID: migrate_to_file_storage
Revises: 60628efa5597
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'migrate_to_file_storage'
down_revision: Union[str, None] = '60628efa5597'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migra de LargeBinary para String (paths de arquivo).

    IMPORTANTE: Esta migration remove as colunas de imagem antigas.
    Se você tiver dados existentes, faça backup antes de executar.
    """
    # Subgrupo: remover colunas antigas e adicionar novas
    op.add_column('subgrupo', sa.Column('icone_grupo_path', sa.String(500), nullable=True))
    op.add_column('subgrupo', sa.Column('bg_path', sa.String(500), nullable=True))

    # Tentar remover colunas antigas (pode falhar se não existirem)
    try:
        op.drop_column('subgrupo', 'icone_grupo')
    except Exception:
        pass
    try:
        op.drop_column('subgrupo', 'bg')
    except Exception:
        pass

    # Membros: remover colunas antigas e adicionar novas
    op.add_column('membros', sa.Column('foto_path', sa.String(500), nullable=True))
    op.add_column('membros', sa.Column('bg_path', sa.String(500), nullable=True))

    try:
        op.drop_column('membros', 'foto')
    except Exception:
        pass
    try:
        op.drop_column('membros', 'bg')
    except Exception:
        pass

    # Publicacao: remover coluna antiga e adicionar nova
    op.add_column('publicacao', sa.Column('image_path', sa.String(500), nullable=True))

    try:
        op.drop_column('publicacao', 'image')
    except Exception:
        pass


def downgrade() -> None:
    """
    Reverte para LargeBinary.

    ATENÇÃO: Esta operação não recupera os dados das imagens!
    """
    # Publicacao
    op.add_column('publicacao', sa.Column('image', sa.LargeBinary(), nullable=True))
    try:
        op.drop_column('publicacao', 'image_path')
    except Exception:
        pass

    # Membros
    op.add_column('membros', sa.Column('foto', sa.LargeBinary(), nullable=True))
    op.add_column('membros', sa.Column('bg', sa.LargeBinary(), nullable=True))
    try:
        op.drop_column('membros', 'foto_path')
    except Exception:
        pass
    try:
        op.drop_column('membros', 'bg_path')
    except Exception:
        pass

    # Subgrupo
    op.add_column('subgrupo', sa.Column('icone_grupo', sa.LargeBinary(), nullable=True))
    op.add_column('subgrupo', sa.Column('bg', sa.LargeBinary(), nullable=True))
    try:
        op.drop_column('subgrupo', 'icone_grupo_path')
    except Exception:
        pass
    try:
        op.drop_column('subgrupo', 'bg_path')
    except Exception:
        pass
