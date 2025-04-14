from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import postgres_helper
from src.api_v1.stats import schemas as stats_schemas, crud as stats_crud

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/campaigns/{campaign_id}")
async def get_campaign_stats(
    campaign_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> stats_schemas.Stat:
    return await stats_crud.get_campaign_stats(
        campaign_id=campaign_id,
        session=session,
    )


@router.get("/advertisers/{advertiser_id}/campaigns")
async def get_advertiser_stat(
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> stats_schemas.Stat:
    return await stats_crud.get_advertiser_stats(
        advertiser_id=advertiser_id,
        session=session,
    )


@router.get("/campaigns/{campaign_id}/daily")
async def get_campaign_daily_stat(
    campaign_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[stats_schemas.DailyStat]:
    return await stats_crud.get_campaign_daily_stat(
        campaign_id=campaign_id,
        session=session,
    )


@router.get("/advertisers/{advertiser_id}/campaigns/daily")
async def get_advertiser_campaigns_daily_stat(
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[stats_schemas.DailyStat]:
    return await stats_crud.get_advertiser_campaigns_daily_stat(
        advertiser_id=advertiser_id,
        session=session,
    )
