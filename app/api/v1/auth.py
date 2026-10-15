from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.auth.schema import (
    AuthCreate,
    AuthResponse,
    AuthUpdate,
    LoginRequest,
    RoleCreate,
    RoleData,
    RoleListResponse,
    RoleResponse,
    RoleUpdate,
    TokenResponse,
)
from app.domain.auth.model import Auths
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auths", tags=["auths"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[Auths, Depends(get_current_user)]


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: AuthCreate, session: SessionDep) -> AuthResponse:
    return await AuthService(session).create_user(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: SessionDep) -> TokenResponse:
    token = await AuthService(session).login(data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AuthResponse)
async def get_me(current_user: CurrentUserDep) -> AuthResponse:
    return current_user


@router.get("/users", response_model=list[AuthResponse])
async def list_users(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AuthResponse]:
    return await AuthService(session).list_users(offset=offset, limit=limit)


@router.get("/users/{user_id}", response_model=AuthResponse)
async def get_user(user_id: UUID, session: SessionDep) -> AuthResponse:
    return await AuthService(session).get_user(user_id)


@router.patch("/users/{user_id}", response_model=AuthResponse)
async def update_user(
    user_id: UUID, data: AuthUpdate, session: SessionDep
) -> AuthResponse:
    return await AuthService(session).update_user(user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: SessionDep) -> Response:
    await AuthService(session).delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    data: RoleCreate, session: SessionDep
) -> RoleResponse:
    role = await AuthService(session).create_role(data)
    return RoleResponse(
        message="Role created successfully",
        data=RoleData.model_validate(role),
    )


@router.get("/roles", response_model=RoleListResponse)
async def list_roles(session: SessionDep) -> RoleListResponse:
    roles = await AuthService(session).list_roles()
    return RoleListResponse(
        message="Roles retrieved successfully",
        data=[RoleData.model_validate(role) for role in roles],
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: UUID, session: SessionDep) -> RoleResponse:
    role = await AuthService(session).get_role(role_id)
    return RoleResponse(
        message="Role retrieved successfully",
        data=RoleData.model_validate(role),
    )


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID, data: RoleUpdate, session: SessionDep
) -> RoleResponse:
    role = await AuthService(session).update_role(role_id, data)
    return RoleResponse(
        message="Role updated successfully",
        data=RoleData.model_validate(role),
    )


@router.delete("/roles/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(role_id: UUID, session: SessionDep) -> Response:
    await AuthService(session).delete_role(role_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Role deleted successfully"},
    )
