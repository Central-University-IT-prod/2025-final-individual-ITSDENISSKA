from uuid import UUID

from fastapi import UploadFile, File
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.advertisers import crud as advertisers_crud
from src.core.utils import s3_helper


async def upload_files(
    files: list[UploadFile],
    advertiser_id: UUID,
    session: AsyncSession,
) -> list[HttpUrl]:
    advertiser = await advertisers_crud.get_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )
    file_urls = []
    for file in files:
        object_name = f"{advertiser_id}/{file.filename}"
        file_url = s3_helper.upload_file(file.file, object_name)
        file_urls.append(file_url)
    return file_urls


async def get_files_by_advertiser(
    advertiser_id: UUID,
    session: AsyncSession,
) -> list[HttpUrl]:
    advertiser = await advertisers_crud.get_advertiser(
        advertiser_id=advertiser_id,
        session=session,
    )
    prefix = f"{advertiser_id}/"
    return s3_helper.list_files_by_prefix(prefix)
