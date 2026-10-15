from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import Conflict, NotFound, Unauthorized
from app.core.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.domain.auth.model import Auths, RoleUser
from app.domain.auth.schema import AuthCreate, AuthUpdate, LoginRequest, RoleCreate, RoleUpdate
from app.repositories.auth_repository import AuthRepository
from app.repositories.role_repository import RoleRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auths = AuthRepository(session)
        self.roles = RoleRepository(session)

    async def create_user(self, data: AuthCreate) -> Auths:
        if await self.auths.get_by_email(data.email):
            raise Conflict("A user with this email already exists.")

        role = await self.roles.get(data.user_role)
        if role is None:
            
            raise NotFound("Role")

        user = Auths(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
            role=role,
        )
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise Conflict("User or role already exists.") from exc
        return await self.auths.get(user.id)  # eager-load the response's role

    async def get_user(self, user_id: UUID) -> Auths:
        user = await self.auths.get(user_id)
        if user is None:
            raise NotFound("User")
        return user

    async def list_users(self, offset: int = 0, limit: int = 100) -> list[Auths]:
        return await self.auths.list(offset=offset, limit=limit)

    async def update_user(self, user_id: UUID, data: AuthUpdate) -> Auths:
        user = await self.get_user(user_id)
        changes = data.model_dump(exclude_unset=True)
        if "password" in changes and changes["password"] is not None:
            changes["password"] = hash_password(changes["password"])
        if "user_role" in changes and changes["user_role"] is not None:
            role = await self.roles.get(changes.pop("user_role"))
            if role is None:
                raise NotFound("Role")
            user.role = role
        for field, value in changes.items():
            setattr(user, field, value)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise Conflict("A user with this email already exists.") from exc
        return await self.get_user(user_id)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user(user_id)
        await self.auths.delete(user)
        await self.session.commit()

    async def create_role(self, data: RoleCreate) -> RoleUser:
        if await self.roles.get_by_name(data.name):
            raise Conflict("A role with this name already exists.")
        role = RoleUser(name=data.name, note=data.note)
        self.session.add(role)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise Conflict("A role with this name already exists.") from exc
        await self.session.refresh(role)
        return role

    async def get_role(self, role_id: UUID) -> RoleUser:
        role = await self.roles.get(role_id)
        if role is None:
            raise NotFound("Role")
        return role

    async def list_roles(self) -> list[RoleUser]:
        return await self.roles.list()

    async def update_role(self, role_id: UUID, data: RoleUpdate) -> RoleUser:
        role = await self.get_role(role_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise Conflict("A role with this name already exists.") from exc
        await self.session.refresh(role)
        return role

    async def delete_role(self, role_id: UUID) -> None:
        role = await self.get_role(role_id)
        user_count = await self.session.scalar(
            select(func.count()).select_from(Auths).where(Auths.user_role == role_id)
        )
        if user_count:
            raise Conflict("Cannot delete a role assigned to users.")
        await self.roles.delete(role)
        await self.session.commit()

    async def login(self, data: LoginRequest) -> str:
        user = await self.auths.get_by_email(data.email)
        if user is None:
            verify_password(data.password, DUMMY_HASH)
            raise Unauthorized()
        if not verify_password(data.password, user.password):
            raise Unauthorized()
        return create_access_token(str(user.id), {"role": user.role.name})
