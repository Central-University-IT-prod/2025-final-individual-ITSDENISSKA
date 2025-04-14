from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import models
from src.api_v1.time import schemas as time_schemas


async def advance_time(
    date_in: time_schemas.Date,
    session: AsyncSession,
) -> time_schemas.Date:
    current_date_row = await session.execute(select(models.CurrentDate))
    current_date_instance = current_date_row.scalar_one_or_none()

    if not current_date_instance:
        new_date = models.CurrentDate(current_date=date_in.current_date)
        session.add(new_date)
        current_date_value = date_in.current_date
    else:
        current_date_instance.current_date = date_in.current_date
        current_date_value = date_in.current_date

    await session.commit()
    return time_schemas.Date(current_date=current_date_value)


async def get_current_date(
    session: AsyncSession,
) -> time_schemas.Date:
    current_date = await session.execute(select(models.CurrentDate))
    current_date = current_date.scalar_one_or_none()
    if current_date is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current date not found",
        )
    return time_schemas.Date(current_date=current_date.current_date)
