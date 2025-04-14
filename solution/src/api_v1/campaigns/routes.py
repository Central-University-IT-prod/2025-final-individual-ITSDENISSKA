import json
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    Body,
    HTTPException,
)
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.data import settings
from src.core.database import postgres_helper
from src.api_v1.campaigns import (
    schemas as campaigns_schemas,
    crud as campaigns_crud,
)
from src.core.utils.llm_utils import llm_functions

router = APIRouter(prefix="/advertisers/{advertiser_id}/campaigns", tags=["Campaigns"])


@router.get("")
async def get_campaign(
    advertiser_id: UUID,
    size: PositiveInt = 10,
    page: PositiveInt = 1,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[campaigns_schemas.Campaign]:
    return await campaigns_crud.get_campaigns(
        advertiser_id=advertiser_id,
        session=session,
        size=size,
        page=page,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign(
    advertiser_id: UUID,
    campaign_in: campaigns_schemas.CampaignCreate,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> campaigns_schemas.Campaign:
    if settings.moderate_ad_text:
        moderate_response = await llm_functions.moderate_text_with_llm(
            ad_text=campaign_in.ad_text,
            ad_title=campaign_in.ad_title,
        )
        if not moderate_response.status:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=moderate_response.reason,
            )
    return await campaigns_crud.create_campaign(
        advertiser_id=advertiser_id,
        campaign_in=campaign_in,
        session=session,
    )


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: UUID,
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> campaigns_schemas.Campaign:
    return await campaigns_crud.get_campaign(
        campaign_id=campaign_id,
        advertiser_id=advertiser_id,
        session=session,
    )


@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: UUID,
    advertiser_id: UUID,
    campaign_in: campaigns_schemas.CampaignUpdate,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> campaigns_schemas.Campaign:
    if settings.moderate_ad_text:
        moderate_response = await llm_functions.moderate_text_with_llm(
            ad_text=campaign_in.ad_text,
            ad_title=campaign_in.ad_title,
        )
        if not moderate_response.status:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=moderate_response.reason,
            )
    return await campaigns_crud.update_campaign(
        campaign_id=campaign_id,
        advertiser_id=advertiser_id,
        campaign_in=campaign_in,
        session=session,
    )


@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_campaign(
    campaign_id: UUID,
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> None:
    await campaigns_crud.delete_campaign(
        campaign_id=campaign_id,
        advertiser_id=advertiser_id,
        session=session,
    )
