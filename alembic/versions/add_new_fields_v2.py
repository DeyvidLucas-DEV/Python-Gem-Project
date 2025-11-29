"""Add email, linkedin, lattes to membros; infograficos to subgrupo; link_externo to publicacao

Revision ID: add_new_fields_v2
Revises: migrate_to_file_storage
Create Date: 2025-11-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_new_fields_v2'
down_revision: Union[str, None] = 'migrate_to_file_storage'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona novos campos às tabelas."""

    # Membros: email, linkedin, lattes
    op.add_column('membros', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('membros', sa.Column('linkedin', sa.String(500), nullable=True))
    op.add_column('membros', sa.Column('lattes', sa.String(500), nullable=True))

    # Subgrupo: infograficos (JSON array de paths)
    op.add_column('subgrupo', sa.Column('infograficos', sa.Text(), nullable=True))

    # Publicacao: link_externo
    op.add_column('publicacao', sa.Column('link_externo', sa.String(1000), nullable=True))


def downgrade() -> None:
    """Remove os novos campos."""

    # Publicacao
    op.drop_column('publicacao', 'link_externo')

    # Subgrupo
    op.drop_column('subgrupo', 'infograficos')

    # Membros
    op.drop_column('membros', 'lattes')
    op.drop_column('membros', 'linkedin')
    op.drop_column('membros', 'email')
