from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import postgres_helper
from src.api_v1.ads import schemas as ads_schemas, crud as ads_crud
from src.core.utils.llm_utils import schemas as llm_schemas, llm_functions

router = APIRouter(prefix="/ads", tags=["Ads"])


@router.get("")
async def get_ad(
    client_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> ads_schemas.Ad:
    return await ads_crud.get_ad(
        client_id=client_id,
        session=session,
    )


@router.post(
    "/{ad_id}/click",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def click_ad(
    ad_id: UUID,
    client_id: Annotated[UUID, Body(embed=True)],
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
):
    await ads_crud.click_ad(
        ad_id=ad_id,
        client_id=client_id,
        session=session,
    )


@router.get("/generate-ad")
async def generate_ad(
    description: str,
) -> llm_schemas.LLMGeneratedAd:
    return await llm_functions.generate_ad_post(
        description=description,
    )
