import uuid

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.documents import DocumentDetailResponse, DocumentResponse
from src.core.security import get_current_user_id
from src.db.database import async_session_factory, get_db
from src.services.document_service import DocumentService
from src.services.ingestion_service import IngestionService

logger = structlog.get_logger()
router = APIRouter()


async def _run_ingestion(document_id: uuid.UUID, file_bytes: bytes) -> None:
    """Background task: runs ingestion with its own DB session after HTTP response is sent."""
    async with async_session_factory() as db:
        service = IngestionService(db)
        await service.ingest(document_id, file_bytes)


@router.post(
    "/collections/{collection_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["documents"],
)
async def upload_document(
    collection_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF to a collection. Returns 202 immediately with status=pending.
    Ingestion (PDF parsing, chunking, embedding) runs as a background task.
    Poll GET /documents/{id} to track progress until status=ready.
    """
    logger.debug(
        "documents.upload.request",
        collection_id=str(collection_id),
        filename=file.filename,
        user_id=str(user_id),
    )

    file_bytes = await file.read()
    service = DocumentService(db)
    doc = await service.upload(
        collection_id=collection_id,
        user_id=user_id,
        filename=file.filename or "upload.pdf",
        content_type=file.content_type or "application/octet-stream",
        file_size=len(file_bytes),
    )

    background_tasks.add_task(_run_ingestion, doc.id, file_bytes)

    logger.info(
        "documents.upload.accepted",
        document_id=str(doc.id),
        filename=doc.filename,
        file_size_bytes=len(file_bytes),
    )
    return doc


@router.get(
    "/collections/{collection_id}/documents",
    response_model=list[DocumentResponse],
    tags=["documents"],
)
async def list_documents(
    collection_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("documents.list.request", collection_id=str(collection_id), user_id=str(user_id))
    service = DocumentService(db)
    return await service.list_for_collection(collection_id, user_id)


@router.get("/{document_id}", response_model=DocumentDetailResponse, tags=["documents"])
async def get_document(
    document_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("documents.get.request", document_id=str(document_id), user_id=str(user_id))
    service = DocumentService(db)
    return await service.get(document_id, user_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["documents"])
async def delete_document(
    document_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("documents.delete.request", document_id=str(document_id), user_id=str(user_id))
    service = DocumentService(db)
    await service.delete(document_id, user_id)
