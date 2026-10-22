from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

ROLES = ("user", "ufficiale", "admin")

def now():
    return datetime.now(timezone.utc)

class Force(Base):
    __tablename__ = "forces"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")

    members: Mapped[list["User"]] = relationship(back_populates="force")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    rank: Mapped[str] = mapped_column(String(50), default="")
    force_id: Mapped[int | None] = mapped_column(ForeignKey("forces.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    force: Mapped["Force | None"] = relationship(back_populates="members")

class Turno(Base):
    __tablename__ = "turni"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    force_id: Mapped[int | None] = mapped_column(ForeignKey("forces.id"), nullable=True)
    screenshot_url: Mapped[str | None] = mapped_column(String(500), nullable=True) # NUOVO CAMPO
    inizio: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    fine: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user: Mapped["User"] = relationship()
    force: Mapped["Force | None"] = relationship()