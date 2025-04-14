from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import postgres_helper, models
from src.api_v1.clients import schemas as clients_schemas


async def get_clients(
    session: AsyncSession,
) -> list[clients_schemas.Client]:
    clients = await session.execute(select(models.Client))
    return [
        clients_schemas.Client.model_validate(client)
        for client in clients.scalars().all()
    ]


async def get_client(
    client_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> clients_schemas.Client:
    client = await session.get(models.Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return clients_schemas.Client.model_validate(client)


async def update_client(
    clients: list[clients_schemas.ClientCreate],
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[clients_schemas.Client]:
    updated_clients = []
    for client_data in clients:
        client = await session.get(models.Client, client_data.client_id)
        if client:
            await session.execute(
                update(models.Client)
                .where(models.Client.client_id == client_data.client_id)
                .values(
                    login=client_data.login,
                    age=client_data.age,
                    location=client_data.location,
                    gender=client_data.gender,
                )
            )
            await session.refresh(client)
            updated_clients.append(clients_schemas.Client.model_validate(client))
        else:
            new_client = models.Client(**client_data.model_dump())
            session.add(new_client)
            await session.flush()
            updated_clients.append(clients_schemas.Client.model_validate(new_client))
    await session.commit()
    return updated_clients
