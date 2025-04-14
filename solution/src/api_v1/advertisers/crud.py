from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import postgres_helper, models
from src.api_v1.advertisers import schemas as advertisers_schemas


async def get_advertisers(
    session: AsyncSession,
) -> list[advertisers_schemas.Advertiser]:
    advertisers = await session.execute(select(models.Advertiser))
    return [
        advertisers_schemas.Advertiser.model_validate(advertiser)
        for advertiser in advertisers.scalars().all()
    ]


async def get_advertiser(
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> advertisers_schemas.Advertiser:
    advertiser = await session.get(models.Advertiser, advertiser_id)
    if not advertiser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advertiser not found",
        )
    return advertisers_schemas.Advertiser.model_validate(advertiser)


async def update_advertiser(
    advertisers: list[advertisers_schemas.AdvertiserCreate],
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[advertisers_schemas.Advertiser]:
    updated_advertisers = []
    for advertiser_data in advertisers:
        advertiser = await session.get(models.Advertiser, advertiser_data.advertiser_id)
        if advertiser:
            await session.execute(
                update(models.Advertiser)
                .where(models.Advertiser.advertiser_id == advertiser_data.advertiser_id)
                .values(name=advertiser_data.name)
            )
            await session.refresh(advertiser)
            updated_advertisers.append(
                advertisers_schemas.Advertiser.model_validate(advertiser)
            )
        else:
            new_advertiser = models.Advertiser(**advertiser_data.model_dump())
            session.add(new_advertiser)
            await session.flush()
            updated_advertisers.append(
                advertisers_schemas.Advertiser.model_validate(new_advertiser)
            )
    await session.commit()
    return updated_advertisers
