import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.documents import DocumentDetailResponse, DocumentResponse
from src.core.config import settings
from src.core.exceptions import CollectionNotFoundError, DocumentNotFoundError, FileTooLargeError, ForbiddenError, InvalidFileTypeError
from src.db.repositories.collection_repository import CollectionRepository
from src.db.repositories.document_repository import DocumentRepository

logger = structlog.get_logger()

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.doc_repo = DocumentRepository(db)
        self.col_repo = CollectionRepository(db)

    async def list_for_collection(self, collection_id: uuid.UUID, user_id: uuid.UUID) -> list[DocumentResponse]:
        collection = await self.col_repo.get_by_id_for_user(collection_id, user_id)
        if not collection:
            raise CollectionNotFoundError(f"Collection {collection_id} not found")

        docs = await self.doc_repo.get_all_for_collection(collection_id)
        return [DocumentResponse.model_validate(d) for d in docs]

    async def get(self, document_id: uuid.UUID, user_id: uuid.UUID) -> DocumentDetailResponse:
        doc = await self.doc_repo.get_by_id_for_user(document_id, user_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        chunk_count = await self.doc_repo.get_chunk_count(document_id)
        response = DocumentDetailResponse.model_validate(doc)
        response.chunk_count = chunk_count
        return response

    async def upload(
        self,
        collection_id: uuid.UUID,
        user_id: uuid.UUID,
        filename: str,
        content_type: str,
        file_size: int,
    ) -> DocumentResponse:
        if content_type not in ("application/pdf", "application/octet-stream") and not filename.lower().endswith(".pdf"):
            raise InvalidFileTypeError("Only PDF files are accepted")
        if file_size > MAX_UPLOAD_BYTES:
            raise FileTooLargeError(f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB")

        collection = await self.col_repo.get_by_id_for_user(collection_id, user_id)
        if not collection:
            raise CollectionNotFoundError(f"Collection {collection_id} not found")

        doc = await self.doc_repo.create(
            collection_id=collection_id,
            user_id=user_id,
            filename=filename,
            file_size_bytes=file_size,
        )
        logger.info("document.upload.created", document_id=str(doc.id), filename=filename, collection_id=str(collection_id))
        return DocumentResponse.model_validate(doc)

    async def delete(self, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        doc = await self.doc_repo.get_by_id_for_user(document_id, user_id)
        if not doc:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        await self.doc_repo.delete(doc)
        logger.info("document.deleted", document_id=str(document_id), user_id=str(user_id))
