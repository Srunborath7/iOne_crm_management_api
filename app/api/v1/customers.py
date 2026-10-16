from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.domain.auth.model import Auths
from app.domain.customers.schema import (
    CustomerCreate,
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"],dependencies=[Depends(get_current_user)])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[Auths, Depends(get_current_user)]


@router.post(
    "/",
    response_model=CustomerDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate, session: SessionDep
) -> CustomerDetailResponse:
    customer = await CustomerService(session).create_customer(data)
    return CustomerDetailResponse(
        message="Customer created successfully",
        data=CustomerResponse.model_validate(customer),
    )


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> CustomerListResponse:
    customers, total = await CustomerService(session).list_customers(
        offset=offset, limit=limit
    )
    return CustomerListResponse(
        message="Customers retrieved successfully",
        data=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/me", response_model=CustomerDetailResponse)
async def get_my_customer(
    session: SessionDep, current_user: CurrentUserDep
) -> CustomerDetailResponse:
    """Return the customer record matching the authenticated user's email."""
    customer = await CustomerService(session).get_customer_by_email(current_user.email)
    return CustomerDetailResponse(
        message="Customer profile retrieved successfully",
        data=CustomerResponse.model_validate(customer),
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: UUID, session: SessionDep
) -> CustomerDetailResponse:
    customer = await CustomerService(session).get_customer(customer_id)
    return CustomerDetailResponse(
        message="Customer retrieved successfully",
        data=CustomerResponse.model_validate(customer),
    )


@router.patch("/{customer_id}", response_model=CustomerDetailResponse)
async def update_customer(
    customer_id: UUID, data: CustomerUpdate, session: SessionDep
) -> CustomerDetailResponse:
    customer = await CustomerService(session).update_customer(customer_id, data)
    return CustomerDetailResponse(
        message="Customer updated successfully",
        data=CustomerResponse.model_validate(customer),
    )


@router.delete("/{customer_id}", status_code=status.HTTP_200_OK)
async def delete_customer(
    customer_id: UUID, session: SessionDep
) -> Response:
    await CustomerService(session).delete_customer(customer_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Customer deleted successfully"},
    )
