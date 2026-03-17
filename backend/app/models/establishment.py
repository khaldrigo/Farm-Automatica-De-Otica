from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, DateTime, Enum, Float, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.review import Review


class EstablishmentStatus(enum.StrEnum):
    PENDING_REVIEW = enum.auto()
    ACTIVE = enum.auto()
    INACTIVE = enum.auto()


class Establishment(Base):
    __tablename__ = "establishments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(100), nullable=True)
    facebook: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_ids: Mapped[list[uuid.UUID] | None] = mapped_column(ARRAY(Uuid), nullable=True)

    embedding: Mapped[list[float] | None] = mapped_column(ARRAY(Float), nullable=True)

    business_hours: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[EstablishmentStatus] = mapped_column(
        Enum(EstablishmentStatus),
        default=EstablishmentStatus.PENDING_REVIEW,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    reviews: Mapped[list[Review]] = relationship("Review", back_populates="establishment")

    __table_args__ = (
        Index("ix_establishments_slug", "slug"),
        Index("ix_establishments_category_ids", "category_ids", postgresql_using="gin"),
    )
