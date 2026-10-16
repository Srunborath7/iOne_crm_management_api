from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr


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
    """Fields required to create a user, with an optional role override."""

    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)
    user_role: UUID | None = None


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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=8, max_length=255)

class MessageResponse(BaseModel):
    message: str
