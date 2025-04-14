from sqlalchemy import Integer
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select, func, and_, or_, desc, distinct, case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import models
from src.api_v1.ads import schemas as ads_schemas
from src.api_v1.time import crud as time_crud
from src.api_v1.clients import crud as clients_crud
from src.api_v1.campaigns import schemas as campaign_schemas
from src.core.utils import enums
from fastapi import HTTPException, status
from uuid import UUID


async def get_ad(client_id: UUID, session: AsyncSession) -> ads_schemas.Ad:
    client = await clients_crud.get_client(client_id=client_id, session=session)
    current_date_result = await time_crud.get_current_date(session=session)
    current_day = current_date_result.current_date

    max_ml_score_subquery = select(func.max(models.MLScore.score)).scalar_subquery()

    is_impressioned_subquery = (
        select(models.UniqueImpression.campaign_id)
        .where(
            models.UniqueImpression.client_id == client_id,
            models.UniqueImpression.campaign_id == models.Campaign.campaign_id,
        )
        .correlate(models.Campaign)
        .exists()
    )
    is_clicked_subquery = (
        select(models.UniqueClick.campaign_id)
        .where(
            models.UniqueClick.client_id == client_id,
            models.UniqueClick.campaign_id == models.Campaign.campaign_id,
        )
        .correlate(models.Campaign)
        .exists()
    )

    stmt = (
        select(models.Campaign)
        .outerjoin(
            models.MLScore,
            and_(
                models.MLScore.client_id == client_id,
                models.MLScore.advertiser_id == models.Campaign.advertiser_id,
            ),
        )
        .outerjoin(
            models.UniqueImpression,
            and_(
                models.UniqueImpression.client_id == client_id,
                models.UniqueImpression.campaign_id == models.Campaign.campaign_id,
            ),
        )
        .join(
            models.Targeting,
            models.Targeting.campaign_id == models.Campaign.campaign_id,
        )
        .where(
            and_(
                models.Campaign.start_date <= current_day,
                models.Campaign.end_date >= current_day,
                models.Campaign.is_deleted == False,
                or_(
                    models.Targeting.gender.is_(None),
                    models.Targeting.gender == client.gender,
                    models.Targeting.gender == enums.ExtendedGenderEnum.ALL,
                ),
                and_(
                    or_(
                        models.Targeting.age_from.is_(None),
                        models.Targeting.age_from <= client.age,
                    ),
                    or_(
                        models.Targeting.age_to.is_(None),
                        models.Targeting.age_to >= client.age,
                    ),
                ),
                or_(
                    models.Targeting.location.is_(None),
                    models.Targeting.location == client.location,
                ),
                models.Campaign.clicks_limit
                > (
                    select(func.count(models.UniqueClick.campaign_id))
                    .where(
                        models.UniqueClick.campaign_id == models.Campaign.campaign_id
                    )
                    .correlate(models.Campaign)
                ),
                models.Campaign.impressions_limit
                > (
                    select(func.count(models.UniqueImpression.campaign_id))
                    .where(
                        models.UniqueImpression.campaign_id
                        == models.Campaign.campaign_id
                    )
                    .correlate(models.Campaign)
                ),
            )
        )
        .order_by(
            desc(
                case(
                    (is_impressioned_subquery, 0),
                    else_=models.Campaign.cost_per_impression,
                )
                + (
                    case(
                        (is_clicked_subquery, 0),
                        else_=models.Campaign.cost_per_click,
                    )
                    * case(
                        (
                            models.MLScore.score.isnot(None),
                            models.MLScore.score / max_ml_score_subquery,
                        ),
                        else_=0,
                    )
                )
            )
        )
        .limit(1)
    )

    result = await session.execute(stmt)
    best_campaign = result.scalar_one_or_none()

    if not best_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available ads matching targeting or limits reached",
        )

    await log_impression(
        client_id=client_id,
        campaign_id=best_campaign.campaign_id,
        cost=best_campaign.cost_per_impression,
        session=session,
        current_date=current_day,
    )

    return ads_schemas.Ad(
        ad_id=best_campaign.campaign_id,
        ad_title=best_campaign.ad_title,
        ad_text=best_campaign.ad_text,
        advertiser_id=best_campaign.advertiser_id,
    )


async def log_impression(
    client_id: UUID,
    campaign_id: UUID,
    cost: float,
    session: AsyncSession,
    current_date: int,
):
    stmt = (
        insert(models.UniqueImpression)
        .values(
            client_id=client_id,
            campaign_id=campaign_id,
            date=current_date,
            cost=cost,
        )
        .on_conflict_do_nothing()
    )
    await session.execute(stmt)
    await session.commit()


async def click_ad(ad_id: UUID, client_id: UUID, session: AsyncSession) -> None:
    client = await clients_crud.get_client(client_id=client_id, session=session)
    campaign = await session.execute(
        select(models.Campaign).where(
            models.Campaign.campaign_id == ad_id, models.Campaign.is_deleted == False
        )
    )
    campaign = campaign.scalar_one_or_none()
    if not campaign:
        return

    unique_click = await session.execute(
        select(models.UniqueClick).where(
            models.UniqueClick.client_id == client.client_id,
            models.UniqueClick.campaign_id == campaign.campaign_id,
        )
    )
    impression = await session.execute(
        select(models.UniqueImpression).where(
            models.UniqueImpression.client_id == client.client_id,
            models.UniqueImpression.campaign_id == campaign.campaign_id,
        )
    )
    impression = impression.scalars().all()
    if not impression:
        return
    unique_click = unique_click.scalar_one_or_none()
    if unique_click:
        return

    current_date = await time_crud.get_current_date(session=session)
    session.add(
        models.UniqueClick(
            client_id=client.client_id,
            campaign_id=campaign.campaign_id,
            date=current_date.current_date,
            cost=campaign.cost_per_click,
        )
    )
    await session.commit()
