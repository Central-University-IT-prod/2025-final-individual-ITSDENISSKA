from uuid import UUID

from fastapi import Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import postgres_helper, models
from src.api_v1.campaigns import schemas as campaigns_schemas
from src.api_v1.advertisers import crud as advertisers_crud


async def get_campaign_by_id(
    campaign_id: UUID,
    advertiser_id: UUID | None,
    session: AsyncSession,
) -> models.Campaign:
    query = (
        select(models.Campaign)
        .options(selectinload(models.Campaign.targeting))
        .where(
            models.Campaign.campaign_id == campaign_id,
            models.Campaign.is_deleted == False,
        )
    )
    result = await session.execute(query)
    campaign = result.scalars().first()
    if campaign is None or (advertiser_id and campaign.advertiser_id != advertiser_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return campaign


async def get_campaigns(
    advertiser_id: UUID,
    size: int,
    page: int,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[campaigns_schemas.Campaign]:
    offset = (page - 1) * size
    query = (
        select(models.Campaign)
        .where(models.Campaign.advertiser_id == advertiser_id)
        .options(selectinload(models.Campaign.targeting))
        .order_by(models.Campaign.start_date.desc())
        .offset(offset)
        .limit(size)
    )
    result = await session.execute(query)
    campaigns = result.scalars().all()
    return [
        campaigns_schemas.Campaign.model_validate(campaign) for campaign in campaigns
    ]


async def create_campaign(
    advertiser_id: UUID,
    campaign_in: campaigns_schemas.CampaignCreate,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> campaigns_schemas.Campaign:
    advertiser = await advertisers_crud.get_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )
    campaign_data = campaign_in.model_dump()
    campaign_data.pop("targeting", None)
    if campaign_in.files is not None:
        campaign_data["files"] = [str(url) for url in campaign_in.files]
    campaign = models.Campaign(
        advertiser_id=advertiser.advertiser_id,
        **campaign_data,
    )
    if campaign_in.targeting is None:
        campaign_in.targeting = campaigns_schemas.TargetingCreate(
            gender=None,
            age_from=None,
            age_to=None,
            location=None,
        )

    targeting = models.Targeting(**campaign_in.targeting.model_dump())
    campaign.targeting = targeting

    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)

    query = (
        select(models.Campaign)
        .options(selectinload(models.Campaign.targeting))
        .where(models.Campaign.campaign_id == campaign.campaign_id)
    )
    result = await session.execute(query)
    campaign_with_targeting = result.scalars().first()
    return campaigns_schemas.Campaign.model_validate(campaign_with_targeting)


async def get_campaign(
    campaign_id: UUID,
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> campaigns_schemas.Campaign:
    campaign = await get_campaign_by_id(
        campaign_id=campaign_id,
        advertiser_id=advertiser_id,
        session=session,
    )
    return campaigns_schemas.Campaign.model_validate(campaign)


async def update_campaign(
    campaign_id: UUID,
    advertiser_id: UUID,
    campaign_in: campaigns_schemas.CampaignUpdate,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> campaigns_schemas.Campaign:
    campaign = await get_campaign_by_id(campaign_id, advertiser_id, session)
    if campaign.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a deleted campaign",
        )
    update_data = campaign_in.model_dump(exclude_unset=True)
    if campaign_in.files:
        update_data["files"] = [str(url) for url in campaign_in.files]
    for field, value in update_data.items():
        if field == "targeting":
            continue
        else:
            setattr(campaign, field, value)

    if "targeting" in update_data and update_data["targeting"]:
        targeting_update_data = update_data["targeting"]
        if campaign.targeting:
            for field, value in targeting_update_data.items():
                setattr(campaign.targeting, field, value)
        else:
            campaign.targeting = models.Targeting(**targeting_update_data)
    await session.commit()
    await session.refresh(campaign)
    return campaigns_schemas.Campaign.model_validate(campaign)


async def delete_campaign(
    campaign_id: UUID,
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> None:
    campaign = await get_campaign_by_id(campaign_id, advertiser_id, session)
    if campaign.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is already deleted",
        )
    campaign.is_deleted = True
    await session.commit()
