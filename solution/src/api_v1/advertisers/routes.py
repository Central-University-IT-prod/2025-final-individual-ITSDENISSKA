from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import postgres_helper
from src.api_v1.advertisers import (
    schemas as advertisers_schemas,
    crud as advertisers_crud,
)

router = APIRouter(prefix="/advertisers", tags=["Advertisers"])


@router.get("")
async def get_advertisers(
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[advertisers_schemas.Advertiser]:
    return await advertisers_crud.get_advertisers(session=session)


@router.get("/{advertiser_id}")
async def get_advertiser(
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> advertisers_schemas.Advertiser:
    return await advertisers_crud.get_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )


@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
)
async def create_advertiser(
    advertisers: list[advertisers_schemas.AdvertiserCreate],
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[advertisers_schemas.Advertiser]:
    return await advertisers_crud.update_advertiser(
        advertisers=advertisers,
        session=session,
    )
