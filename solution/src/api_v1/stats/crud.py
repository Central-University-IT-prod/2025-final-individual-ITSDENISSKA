from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.api_v1.stats import schemas as stats_schemas
from src.api_v1.campaigns import crud as campaigns_crud
from src.api_v1.advertisers import crud as advertisers_crud


async def get_campaign_stats(
    campaign_id: UUID,
    session: AsyncSession,
) -> stats_schemas.Stat:
    campaign = await campaigns_crud.get_campaign_by_id(
        campaign_id=campaign_id,
        advertiser_id=None,
        session=session,
    )

    impressions_query = select(
        func.count(models.UniqueImpression.client_id).label("impressions_count"),
        func.sum(models.UniqueImpression.cost).label("spent_impressions"),
    ).where(models.UniqueImpression.campaign_id == campaign.campaign_id)

    impressions_result = await session.execute(impressions_query)
    impressions_data = impressions_result.first()

    clicks_query = select(
        func.count(models.UniqueClick.client_id).label("clicks_count"),
        func.sum(models.UniqueClick.cost).label("spent_clicks"),
    ).where(models.UniqueClick.campaign_id == campaign.campaign_id)

    clicks_result = await session.execute(clicks_query)
    clicks_data = clicks_result.first()

    impressions_count = (
        impressions_data.impressions_count
        if impressions_data and impressions_data.impressions_count
        else 0
    )
    clicks_count = (
        clicks_data.clicks_count if clicks_data and clicks_data.clicks_count else 0
    )
    conversion = (
        (clicks_count / impressions_count * 100) if impressions_count > 0 else 0
    )
    spent_impressions = (
        impressions_data.spent_impressions
        if impressions_data and impressions_data.spent_impressions
        else 0
    )
    spent_clicks = (
        clicks_data.spent_clicks if clicks_data and clicks_data.spent_clicks else 0
    )
    spent_total = spent_impressions + spent_clicks

    return stats_schemas.Stat(
        impressions_count=impressions_count,
        clicks_count=clicks_count,
        conversion=conversion,
        spent_impressions=spent_impressions,
        spent_clicks=spent_clicks,
        spent_total=spent_total,
    )


async def get_advertiser_stats(
    advertiser_id: UUID,
    session: AsyncSession,
) -> stats_schemas.Stat:
    advertiser = await advertisers_crud.get_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )
    impressions_query = (
        select(
            func.count(models.UniqueImpression.client_id).label("impressions_count"),
            func.sum(func.coalesce(models.UniqueImpression.cost, 0)).label(
                "spent_impressions"
            ),
        )
        .join(
            models.Campaign,
            models.UniqueImpression.campaign_id == models.Campaign.campaign_id,
        )
        .where(models.Campaign.advertiser_id == advertiser.advertiser_id)
    )
    impressions_result = await session.execute(impressions_query)
    impressions_data = impressions_result.first()

    clicks_query = (
        select(
            func.count(models.UniqueClick.client_id).label("clicks_count"),
            func.sum(models.UniqueClick.cost).label("spent_clicks"),
        )
        .join(
            models.Campaign,
            models.UniqueClick.campaign_id == models.Campaign.campaign_id,
        )
        .where(models.Campaign.advertiser_id == advertiser.advertiser_id)
    )

    clicks_result = await session.execute(clicks_query)
    clicks_data = clicks_result.first()

    impressions_count = (
        impressions_data.impressions_count
        if impressions_data and impressions_data.impressions_count
        else 0
    )
    clicks_count = (
        clicks_data.clicks_count if clicks_data and clicks_data.clicks_count else 0
    )
    conversion = (
        (clicks_count / impressions_count * 100) if impressions_count > 0 else 0
    )
    spent_impressions = (
        impressions_data.spent_impressions
        if impressions_data and impressions_data.spent_impressions
        else 0
    )
    spent_clicks = (
        clicks_data.spent_clicks if clicks_data and clicks_data.spent_clicks else 0
    )
    spent_total = (spent_impressions or 0) + (spent_clicks or 0)

    return stats_schemas.Stat(
        impressions_count=impressions_count,
        clicks_count=clicks_count,
        conversion=conversion,
        spent_impressions=spent_impressions,
        spent_clicks=spent_clicks,
        spent_total=spent_total,
    )


async def get_campaign_daily_stat(
    campaign_id: UUID,
    session: AsyncSession,
) -> list[stats_schemas.DailyStat]:
    campaign = await campaigns_crud.get_campaign_by_id(
        campaign_id=campaign_id,
        advertiser_id=None,
        session=session,
    )
    impressions_query = (
        select(
            models.UniqueImpression.date,
            func.count(models.UniqueImpression.client_id).label("impressions_count"),
            func.sum(models.UniqueImpression.cost).label("spent_impressions"),
        )
        .where(models.UniqueImpression.campaign_id == campaign.campaign_id)
        .group_by(models.UniqueImpression.date)
    )

    impressions_result = await session.execute(impressions_query)
    impressions_data = impressions_result.all()

    clicks_query = (
        select(
            models.UniqueClick.date,
            func.count(models.UniqueClick.client_id).label("clicks_count"),
            func.sum(models.UniqueClick.cost).label("spent_clicks"),
        )
        .where(models.UniqueClick.campaign_id == campaign.campaign_id)
        .group_by(models.UniqueClick.date)
    )

    clicks_result = await session.execute(clicks_query)
    clicks_data = clicks_result.all()

    daily_stats = {}
    for date, impressions_count, spent_impressions in impressions_data:
        daily_stats[date] = {
            "impressions_count": impressions_count,
            "spent_impressions": spent_impressions,
            "clicks_count": 0,
            "spent_clicks": 0,
        }

    for date, clicks_count, spent_clicks in clicks_data:
        if date in daily_stats:
            daily_stats[date]["clicks_count"] = clicks_count
            daily_stats[date]["spent_clicks"] = spent_clicks
        else:
            daily_stats[date] = {
                "impressions_count": 0,
                "spent_impressions": 0,
                "clicks_count": clicks_count,
                "spent_clicks": spent_clicks,
            }

    result = []
    for date, stats in daily_stats.items():
        impressions_count = stats["impressions_count"]
        clicks_count = stats["clicks_count"]
        conversion = (
            (clicks_count / impressions_count * 100) if impressions_count > 0 else 0
        )
        result.append(
            stats_schemas.DailyStat(
                date=date,
                impressions_count=impressions_count,
                clicks_count=clicks_count,
                conversion=conversion,
                spent_impressions=stats["spent_impressions"],
                spent_clicks=stats["spent_clicks"],
                spent_total=(stats["spent_impressions"] or 0)
                + (stats["spent_clicks"] or 0),
            )
        )

    return result


async def get_advertiser_campaigns_daily_stat(
    advertiser_id: UUID,
    session: AsyncSession,
) -> list[stats_schemas.DailyStat]:
    advertiser = await advertisers_crud.get_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )
    impressions_query = (
        select(
            models.UniqueImpression.date,
            func.count(models.UniqueImpression.client_id).label("impressions_count"),
            func.sum(models.UniqueImpression.cost).label("spent_impressions"),
        )
        .join(
            models.Campaign,
            models.UniqueImpression.campaign_id == models.Campaign.campaign_id,
        )
        .where(models.Campaign.advertiser_id == advertiser.advertiser_id)
        .group_by(models.UniqueImpression.date)
    )

    impressions_result = await session.execute(impressions_query)
    impressions_data = impressions_result.all()

    clicks_query = (
        select(
            models.UniqueClick.date,
            func.count(models.UniqueClick.client_id).label("clicks_count"),
            func.sum(models.UniqueClick.cost).label("spent_clicks"),
        )
        .join(
            models.Campaign,
            models.UniqueClick.campaign_id == models.Campaign.campaign_id,
        )
        .where(models.Campaign.advertiser_id == advertiser.advertiser_id)
        .group_by(models.UniqueClick.date)
    )

    clicks_result = await session.execute(clicks_query)
    clicks_data = clicks_result.all()

    daily_stats = {}
    for date, impressions_count, spent_impressions in impressions_data:
        daily_stats[date] = {
            "impressions_count": impressions_count,
            "spent_impressions": spent_impressions,
            "clicks_count": 0,
            "spent_clicks": 0,
        }

    for date, clicks_count, spent_clicks in clicks_data:
        if date in daily_stats:
            daily_stats[date]["clicks_count"] = clicks_count
            daily_stats[date]["spent_clicks"] = spent_clicks
        else:
            daily_stats[date] = {
                "impressions_count": 0,
                "spent_impressions": 0,
                "clicks_count": clicks_count,
                "spent_clicks": spent_clicks,
            }

    result = []
    for date, stats in daily_stats.items():
        impressions_count = stats["impressions_count"]
        clicks_count = stats["clicks_count"]
        conversion = (
            (clicks_count / impressions_count * 100) if impressions_count > 0 else 0
        )
        result.append(
            stats_schemas.DailyStat(
                date=date,
                impressions_count=impressions_count,
                clicks_count=clicks_count,
                conversion=conversion,
                spent_impressions=stats["spent_impressions"],
                spent_clicks=stats["spent_clicks"],
                spent_total=(stats["spent_impressions"] or 0)
                + (stats["spent_clicks"] or 0),
            )
        )

    return result
