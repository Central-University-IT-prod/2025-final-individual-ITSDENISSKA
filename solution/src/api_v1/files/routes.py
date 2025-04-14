from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.files import crud as files_crud
from src.core.database import postgres_helper

router = APIRouter(prefix="/flies", tags=["Files"])


@router.post("/upload")
async def upload_files(
    advertiser_id: UUID,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[HttpUrl]:
    return await files_crud.upload_files(
        files=files,
        advertiser_id=advertiser_id,
        session=session,
    )


@router.get("/{advertiser_id}")
async def get_files_by_advertiser_endpoint(
    advertiser_id: UUID,
    session: AsyncSession = Depends(postgres_helper.scoped_session_dependency),
) -> list[HttpUrl]:
    return await files_crud.get_files_by_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )
