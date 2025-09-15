from datetime import datetime, timezone

from sqlalchemy import String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class AuditFieldsMixin:
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str | None] = mapped_column(
        String, nullable=True, doc="updated by"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(timezone.utc), doc="created at"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=func.now(timezone.utc),
        onupdate=func.now(timezone.utc),
        doc="updated at",
    )
