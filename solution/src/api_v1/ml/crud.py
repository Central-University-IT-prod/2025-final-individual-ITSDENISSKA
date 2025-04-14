from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import postgres_helper, models

from src.api_v1.ml import schemas as ml_schemas
from src.api_v1.clients import crud as clients_crud
from src.api_v1.advertisers import crud as advertisers_crud


async def get_ml_score(
    client_id: UUID,
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> ml_schemas.MLScore:
    query = select(models.MLScore).where(
        models.MLScore.client_id == client_id,
        models.MLScore.advertiser_id == advertiser_id,
    )
    result = await session.execute(query)
    ml_score = result.scalar_one_or_none()
    if not ml_score:
        return ml_schemas.MLScore(
            client_id=client_id,
            advertiser_id=advertiser_id,
            score=0,
        )
    return ml_schemas.MLScore.model_validate(ml_score)


async def update_ml_score(
    ml_score_in: ml_schemas.MLScoreCreate,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> ml_schemas.MLScore:
    await clients_crud.get_client(
        client_id=ml_score_in.client_id,
        session=session,
    )
    await advertisers_crud.get_advertiser(
        advertiser_id=ml_score_in.advertiser_id,
        session=session,
    )
    query = select(models.MLScore).where(
        models.MLScore.client_id == ml_score_in.client_id,
        models.MLScore.advertiser_id == ml_score_in.advertiser_id,
    )
    result = await session.execute(query)
    ml_score = result.scalar_one_or_none()
    if ml_score:
        ml_score.score = ml_score_in.score
        await session.commit()
        await session.refresh(ml_score)
    else:
        new_ml_score = models.MLScore(**ml_score_in.model_dump())
        session.add(new_ml_score)
        await session.commit()
        await session.refresh(new_ml_score)
        ml_score = new_ml_score
    return ml_schemas.MLScore.model_validate(ml_score)
