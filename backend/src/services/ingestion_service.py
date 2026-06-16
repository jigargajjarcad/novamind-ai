import uuid
from datetime import datetime, timezone

import fitz  # PyMuPDF
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import DocumentProcessingError
from src.db.repositories.document_repository import DocumentRepository
from src.models.document import ChunkEmbedding, DocumentChunk
from src.services.anthropic_service import AnthropicService

logger = structlog.get_logger()

# 1 token ≈ 4 characters — sufficient precision for chunk size targeting
_CHARS_PER_TOKEN = 4


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.doc_repo = DocumentRepository(db)
        self.anthropic = AnthropicService()

    async def ingest(self, document_id: uuid.UUID, file_bytes: bytes) -> None:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            logger.error("ingestion.document_not_found", document_id=str(document_id))
            return

        try:
            await self.doc_repo.update_status(doc, status="processing")
            logger.info(
                "document.ingestion.started",
                document_id=str(document_id),
                filename=doc.filename,
                file_size_bytes=len(file_bytes),
            )

            pages = self._parse_pdf(file_bytes)
            if not pages:
                raise DocumentProcessingError(
                    "No text could be extracted from this PDF. "
                    "Scanned PDFs without OCR are not supported."
                )

            chunks = self._chunk_text(pages, document_id)
            logger.info(
                "document.ingestion.chunked",
                document_id=str(document_id),
                page_count=len(pages),
                chunk_count=len(chunks),
            )

            # Persist chunks first so they have IDs
            saved_chunks = await self.doc_repo.create_chunks(chunks)

            embeddings = await self._generate_embeddings(saved_chunks, document_id)
            await self.doc_repo.create_embeddings(embeddings)

            await self.doc_repo.update_status(
                doc,
                status="ready",
                page_count=len(pages),
                processed_at=datetime.now(timezone.utc),
            )
            logger.info(
                "document.ingestion.completed",
                document_id=str(document_id),
                chunk_count=len(chunks),
                embedding_count=len(embeddings),
            )

        except Exception as e:
            logger.error(
                "document.ingestion.failed",
                document_id=str(document_id),
                error=str(e),
                exc_info=True,
            )
            await self.doc_repo.update_status(doc, status="failed", error_message=str(e))

    # ------------------------------------------------------------------
    # PDF Parsing
    # ------------------------------------------------------------------

    def _parse_pdf(self, file_bytes: bytes) -> list[dict]:
        """Extract text per page using PyMuPDF. Returns [{page_number, text}]."""
        pages: list[dict] = []
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                cleaned = text.strip()
                if cleaned:
                    pages.append({"page_number": page_num, "text": cleaned})
        return pages

    # ------------------------------------------------------------------
    # Text Chunking — paragraph-aware sliding window
    # ------------------------------------------------------------------

    def _chunk_text(self, pages: list[dict], document_id: uuid.UUID) -> list[DocumentChunk]:
        """
        Split extracted page text into overlapping chunks.

        Strategy: flatten pages → paragraphs, then apply a sliding window that
        respects paragraph boundaries. Chunk size and overlap are read from
        settings (CHUNK_SIZE_TOKENS / CHUNK_OVERLAP_TOKENS).
        """
        max_chars = settings.CHUNK_SIZE_TOKENS * _CHARS_PER_TOKEN
        overlap_chars = settings.CHUNK_OVERLAP_TOKENS * _CHARS_PER_TOKEN

        # Flatten all pages into (text, page_number) paragraph tuples
        paragraphs: list[tuple[str, int]] = []
        for page in pages:
            for para in page["text"].split("\n\n"):
                clean = para.strip()
                if len(clean) > 10:  # skip blank lines and stray punctuation
                    paragraphs.append((clean, page["page_number"]))

        if not paragraphs:
            return []

        chunks: list[DocumentChunk] = []
        chunk_index = 0
        start = 0  # paragraph index where the current chunk begins

        while start < len(paragraphs):
            body = ""
            end = start

            # Accumulate paragraphs until we'd exceed max_chars
            while end < len(paragraphs):
                para_text, _ = paragraphs[end]
                candidate = (body + "\n\n" + para_text) if body else para_text
                if body and len(candidate) > max_chars:
                    break
                body = candidate
                end += 1

            page_num = paragraphs[start][1]
            chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    content=body,
                    chunk_index=chunk_index,
                    page_number=page_num,
                )
            )
            chunk_index += 1

            if end >= len(paragraphs):
                break

            # Step back from `end` by overlap_chars to find the overlap boundary,
            # always at a paragraph boundary to avoid mid-sentence splits.
            chars_accumulated = 0
            next_start = end
            for j in range(end - 1, start, -1):
                chars_accumulated += len(paragraphs[j][0]) + 2  # +2 for \n\n
                if chars_accumulated >= overlap_chars:
                    next_start = j
                    break

            # Guarantee forward progress — never re-process the same paragraph
            if next_start <= start:
                next_start = start + 1

            start = next_start

        return chunks

    # ------------------------------------------------------------------
    # Embedding Generation
    # ------------------------------------------------------------------

    async def _generate_embeddings(
        self,
        chunks: list[DocumentChunk],
        document_id: uuid.UUID,
    ) -> list[ChunkEmbedding]:
        texts = [c.content for c in chunks]
        vectors = await self.anthropic.embed(texts, input_type="document")

        if len(vectors) != len(chunks):
            raise DocumentProcessingError(
                f"Embedding count mismatch: expected {len(chunks)}, got {len(vectors)}"
            )

        return [
            ChunkEmbedding(
                chunk_id=chunk.id,
                embedding=vector,
                model_used="voyage-3",
            )
            for chunk, vector in zip(chunks, vectors)
        ]
