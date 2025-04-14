from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import postgres_helper
from src.api_v1.clients import schemas as clients_schemas, crud as clients_crud

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("")
async def get_clients(
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[clients_schemas.Client]:
    return await clients_crud.get_clients(session=session)


@router.get("/{client_id}")
async def get_client(
    client_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> clients_schemas.Client:
    return await clients_crud.get_client(
        client_id=client_id,
        session=session,
    )


@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
    clients: list[clients_schemas.ClientCreate],
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[clients_schemas.Client]:
    return await clients_crud.update_client(
        clients=clients,
        session=session,
    )
