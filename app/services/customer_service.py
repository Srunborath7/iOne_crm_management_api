from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import Conflict, NotFound
from app.domain.customers.model import Customer
from app.domain.customers.schema import CustomerCreate, CustomerUpdate
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    """Business-logic layer for customer operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customers = CustomerRepository(session)

    async def create_customer(self, data: CustomerCreate) -> Customer:
        if data.email and await self.customers.get_by_email(data.email):
            raise Conflict("A customer with this email already exists.")
        if data.phone and await self.customers.get_by_phone(data.phone):
            raise Conflict("A customer with this phone already exists.")

        customer = Customer(**data.model_dump())
        self.session.add(customer)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise Conflict("Duplicate email or phone.") from exc
        await self.session.refresh(customer)
        return customer

    async def get_customer(self, customer_id: UUID) -> Customer:
        customer = await self.customers.get(customer_id)
        if customer is None:
            raise NotFound("Customer")
        return customer

    async def list_customers(
        self, offset: int = 0, limit: int = 100
    ) -> tuple[list[Customer], int]:
        customers = await self.customers.list(offset=offset, limit=limit)
        total = await self.customers.count()
        return customers, total

    async def update_customer(
        self, customer_id: UUID, data: CustomerUpdate
    ) -> Customer:
        customer = await self.get_customer(customer_id)
        changes = data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            setattr(customer, field, value)

        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise Conflict("Duplicate email or phone.") from exc
        await self.session.refresh(customer)
        return customer

    async def delete_customer(self, customer_id: UUID) -> None:
        customer = await self.get_customer(customer_id)
        await self.customers.delete(customer)
        await self.session.commit()
