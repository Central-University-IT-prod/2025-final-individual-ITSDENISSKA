from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import postgres_helper

from src.api_v1.ml import crud as ml_crud, schemas as ml_schemas

router = APIRouter(prefix="/ml-scores", tags=["Advertisers"])


@router.post("")
async def add_or_update_ml_score(
    ml_score_in: ml_schemas.MLScoreCreate,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> None:
    await ml_crud.update_ml_score(
        ml_score_in=ml_score_in,
        session=session,
    )
