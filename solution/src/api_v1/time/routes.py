from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import postgres_helper
from src.api_v1.time import schemas as time_schemas, crud as time_crud

router = APIRouter(prefix="/time", tags=["Time"])


@router.post("/advance")
async def advance_time(
    date_in: time_schemas.Date,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> time_schemas.Date:
    return await time_crud.advance_time(
        date_in=date_in,
        session=session,
    )
