from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    """Fields required to create a role."""

    name: str = Field(min_length=1, max_length=10)
    note: str | None = Field(default=None, max_length=255)


class RoleUpdate(BaseModel):
    """Fields that may be changed on a role."""

    name: str | None = Field(default=None, min_length=1, max_length=10)
    note: str | None = Field(default=None, max_length=255)


class RoleData(BaseModel):
    """Role fields returned inside a response envelope."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    note: str | None = None


class RoleResponse(BaseModel):
    """Standard role response envelope."""

    message: str
    data: RoleData


class RoleListResponse(BaseModel):
    message: str
    data: list[RoleData]


class AuthCreate(BaseModel):
    """Fields required to create a user and assign an existing role."""

    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)
    user_role: UUID


class AuthUpdate(BaseModel):
    """Fields that may be changed on a user."""

    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: str | None = Field(default=None, min_length=1, max_length=50)
    password: str | None = Field(default=None, min_length=1, max_length=255)
    user_role: UUID | None = None


class AuthResponse(BaseModel):
    """Public user representation; deliberately excludes the password."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    role: RoleData

class LoginRequest(BaseModel):
    """Credentials submitted at login."""
 
    email: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)
 
 
class TokenResponse(BaseModel):
    """Bearer token returned after a successful login."""
 
    access_token: str
    token_type: str = "bearer"

