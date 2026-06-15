import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.repositories.document_repository import DocumentRepository
from src.models.document import DocumentChunk

logger = structlog.get_logger()


class IngestionService:
    """
    Week 2: PDF ingestion pipeline.
    parse_pdf → chunk_text → generate_embeddings → store → mark ready
    """

    def __init__(self, db: AsyncSession):
        self.doc_repo = DocumentRepository(db)

    async def ingest(self, document_id: uuid.UUID, file_bytes: bytes) -> None:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            logger.error("ingestion.document_not_found", document_id=str(document_id))
            return

        try:
            await self.doc_repo.update_status(doc, status="processing")
            logger.info("document.ingestion.started", document_id=str(document_id), filename=doc.filename)

            pages = self._parse_pdf(file_bytes)
            chunks = self._chunk_text(pages, document_id)
            # embeddings will be generated via AnthropicService in Week 2

            await self.doc_repo.create_chunks(chunks)
            await self.doc_repo.update_status(
                doc,
                status="ready",
                page_count=len(pages),
                processed_at=datetime.now(timezone.utc),
            )
            logger.info("document.ingestion.completed", document_id=str(document_id), chunks=len(chunks))

        except Exception as e:
            logger.error("document.ingestion.failed", document_id=str(document_id), error=str(e))
            await self.doc_repo.update_status(doc, status="failed", error_message=str(e))

    def _parse_pdf(self, file_bytes: bytes) -> list[dict]:
        # Week 2: PyMuPDF parsing implementation
        raise NotImplementedError("PDF parsing implemented in Week 2")

    def _chunk_text(self, pages: list[dict], document_id: uuid.UUID) -> list[DocumentChunk]:
        # Week 2: paragraph-aware chunking with configurable size/overlap
        raise NotImplementedError("Text chunking implemented in Week 2")
