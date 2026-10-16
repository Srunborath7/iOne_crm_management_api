import uuid
from datetime import datetime 
from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, func, UUID

class Auths(Base):
    __tablename__ = "auths"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("role_users.id"),nullable=False)
    role: Mapped["RoleUser"] = relationship(back_populates="users")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False,)
    password_reset_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
   
class RoleUser(Base):
    __tablename__ = "role_users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    note: Mapped[str] = mapped_column(String(255), nullable=True)
    users: Mapped[list["Auths"]] = relationship(back_populates="role")
