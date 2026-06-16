import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import ChunkEmbedding, Document, DocumentChunk


@dataclass
class ChunkSearchResult:
    """Flat result from the pgvector similarity search, includes document filename."""
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    content: str
    chunk_index: int
    page_number: int | None
    distance: float  # cosine distance — lower is more similar


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def get_by_id_for_user(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_for_collection(self, collection_id: uuid.UUID) -> list[Document]:
        result = await self.db.execute(
            select(Document).where(Document.collection_id == collection_id).order_by(Document.uploaded_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        collection_id: uuid.UUID,
        user_id: uuid.UUID,
        filename: str,
        file_size_bytes: int,
    ) -> Document:
        doc = Document(
            collection_id=collection_id,
            user_id=user_id,
            filename=filename,
            file_size_bytes=file_size_bytes,
            status="pending",
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def update_status(
        self,
        document: Document,
        status: str,
        page_count: int | None = None,
        error_message: str | None = None,
        processed_at: datetime | None = None,
    ) -> Document:
        document.status = status
        if page_count is not None:
            document.page_count = page_count
        if error_message is not None:
            document.error_message = error_message
        if processed_at is not None:
            document.processed_at = processed_at
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()

    async def get_chunk_count(self, document_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        return result.scalar_one()

    async def create_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.db.add_all(chunks)
        await self.db.commit()
        return chunks

    async def create_embeddings(self, embeddings: list[ChunkEmbedding]) -> list[ChunkEmbedding]:
        self.db.add_all(embeddings)
        await self.db.commit()
        return embeddings

    async def search_similar_chunks(
        self,
        collection_id: uuid.UUID,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[ChunkSearchResult]:
        """
        Cosine similarity search via pgvector HNSW index.
        Returns results ordered by ascending distance (most similar first).
        Only searches chunks from status='ready' documents in the given collection.
        """
        sql = text("""
            SELECT
                dc.id          AS chunk_id,
                dc.document_id,
                d.filename,
                dc.content,
                dc.chunk_index,
                dc.page_number,
                ce.embedding <=> CAST(:query_vec AS vector) AS distance
            FROM document_chunks dc
            JOIN chunk_embeddings ce ON dc.id = ce.chunk_id
            JOIN documents d ON dc.document_id = d.id
            WHERE d.collection_id = CAST(:collection_id AS uuid)
              AND d.status = 'ready'
            ORDER BY distance ASC
            LIMIT :top_k
        """)

        result = await self.db.execute(
            sql,
            {
                "query_vec": str(query_embedding),
                "collection_id": str(collection_id),
                "top_k": top_k,
            },
        )

        return [
            ChunkSearchResult(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                filename=row.filename,
                content=row.content,
                chunk_index=row.chunk_index,
                page_number=row.page_number,
                distance=float(row.distance),
            )
            for row in result.fetchall()
        ]
