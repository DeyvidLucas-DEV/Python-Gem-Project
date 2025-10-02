from sqlalchemy import func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from app.core.database import Base


class TimestampMixin:
    """Mixin para campos de timestamp automáticos."""

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )