# PRD — NovaMind AI (Document Intelligence Platform)

**Version:** 1.0  
**Author:** Jigar Gajjar  
**Status:** Active  
**Last Updated:** June 2026

---

## 1. Project Overview

### What It Is
NovaMind AI is a full-stack document intelligence platform powered by RAG (Retrieval Augmented Generation). Users upload PDF documents, organize them into collections, and ask natural language questions. The system retrieves the most relevant content and returns accurate, cited answers grounded in the uploaded documents.

### Problem It Solves
LLMs like Claude have a knowledge cutoff and no access to private documents. NovaMind bridges that gap — giving users the ability to have intelligent, accurate conversations with their own documents without hallucinations, because every answer is grounded in real content with citations.

### Target Users
- **Developers / Technical users** — evaluating RAG architecture, using it as a reference implementation
- **Business users / Non-technical** — uploading contracts, reports, manuals, and querying them conversationally

### Success Criteria
- User uploads a PDF and can ask questions within 30 seconds of upload completing
- Answers include citations pointing to the exact source paragraph
- Query response time under 3 seconds end to end
- System handles PDFs up to 200 pages without degradation
- Cost per query tracked and visible in admin panel

---

## 2. Technical Architecture

### System Overview
```
User (Browser)
     ↓
React Frontend (Vercel)
     ↓
FastAPI Backend (Railway)
     ├── Document Ingestion Pipeline
     │     ├── PDF Parser
     │     ├── Text Chunker
     │     └── Embedding Generator (Anthropic)
     ├── RAG Query Pipeline
     │     ├── Query Embedder
     │     ├── Vector Search (pgvector)
     │     ├── Reranker
     │     └── Claude Answer Generator
     └── PostgreSQL + pgvector (Railway)
```

### Deployment
- **Frontend:** Vercel (React, free tier)
- **Backend:** Railway (FastAPI + PostgreSQL + pgvector)
- **Local Dev:** Docker Compose (all services)
- **CI/CD:** GitHub Actions → auto deploy on merge to main

### Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React, TailwindCSS, React Query |
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 15 + pgvector extension |
| AI | Anthropic Claude API (claude-sonnet-4-6) |
| Embeddings | Anthropic text-embedding model |
| PDF Parsing | PyMuPDF (fitz) |
| ORM | SQLAlchemy + Alembic |
| Auth | JWT (python-jose) |
| Containerization | Docker + Docker Compose |

---

## 3. Database Design

### Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Collections (folders for organizing documents)
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT,
    page_count INTEGER,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, ready, failed
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Document Chunks (text split from documents)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    char_start INTEGER,
    char_end INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunk Embeddings (pgvector)
CREATE TABLE chunk_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding VECTOR(1536) NOT NULL,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON chunk_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    collection_id UUID REFERENCES collections(id) ON DELETE SET NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Message Citations (which chunks were used for each answer)
CREATE TABLE message_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES chat_messages(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    citation_index INTEGER -- order citations appear in the answer
);

-- Query Logs (cost and performance tracking)
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    chunks_retrieved INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd DECIMAL(10, 6),
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Design

### Base URL
- Local: `http://localhost:8000/api/v1`
- Production: `https://api.novamind.railway.app/api/v1`

### Auth Strategy
JWT Bearer tokens. All endpoints except `/auth/*` require `Authorization: Bearer <token>` header.

### Error Response Standard
```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document with id xyz does not exist",
    "details": {}
  }
}
```

---

### Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Get current user profile |

**POST /auth/register**
```json
Request:  { "email": "user@example.com", "password": "...", "full_name": "Jigar" }
Response: { "user": { "id": "...", "email": "...", "full_name": "..." }, "token": "..." }
```

**POST /auth/login**
```json
Request:  { "email": "user@example.com", "password": "..." }
Response: { "token": "...", "expires_at": "..." }
```

---

### Collections Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/collections` | List all collections for current user |
| POST | `/collections` | Create a new collection |
| GET | `/collections/{id}` | Get collection with documents |
| PUT | `/collections/{id}` | Update collection name/description |
| DELETE | `/collections/{id}` | Delete collection and all documents |

**POST /collections**
```json
Request:  { "name": "Legal Contracts", "description": "Q4 2025 contracts" }
Response: { "id": "...", "name": "...", "description": "...", "created_at": "..." }
```

---

### Documents Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/collections/{id}/documents` | Upload PDF to collection |
| GET | `/collections/{id}/documents` | List documents in collection |
| GET | `/documents/{id}` | Get document details and status |
| DELETE | `/documents/{id}` | Delete document and its chunks |

**POST /collections/{id}/documents**
```
Content-Type: multipart/form-data
Body: file (PDF, max 50MB)
Response: { "id": "...", "filename": "...", "status": "processing", "uploaded_at": "..." }
```

**GET /documents/{id}**
```json
Response: {
  "id": "...",
  "filename": "contract.pdf",
  "status": "ready",
  "page_count": 24,
  "chunk_count": 87,
  "file_size_bytes": 1240000,
  "processed_at": "..."
}
```

---

### Chat Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat/sessions` | Create new chat session |
| GET | `/chat/sessions` | List all chat sessions |
| GET | `/chat/sessions/{id}` | Get session with message history |
| POST | `/chat/sessions/{id}/messages` | Send a message, get streamed response |
| DELETE | `/chat/sessions/{id}` | Delete chat session |

**POST /chat/sessions**
```json
Request:  { "collection_id": "...", "name": "Contract Review Session" }
Response: { "id": "...", "collection_id": "...", "name": "...", "created_at": "..." }
```

**POST /chat/sessions/{id}/messages**
```json
Request:  { "content": "What are the termination clauses in the contract?" }
Response: Server-Sent Events (SSE) stream
  event: chunk     → streaming answer text
  event: citations → array of cited chunks with page numbers
  event: done      → final message with full content + cost info
```

---

### Admin Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/usage` | Total tokens used and cost per user |
| GET | `/admin/queries` | Query log with latency and cost |

---

## 5. Frontend Design

### Pages

```
/                    → Landing page (hero, features, CTA)
/login               → Login form
/register            → Register form
/dashboard           → Collections overview
/collections/:id     → Collection detail (documents list + upload)
/chat/:sessionId     → Chat interface
/admin               → Usage and cost dashboard
```

### Component Structure

```
src/
├── pages/
│   ├── Landing.jsx
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Dashboard.jsx
│   ├── Collection.jsx
│   ├── Chat.jsx
│   └── Admin.jsx
├── components/
│   ├── layout/
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   └── PageWrapper.jsx
│   ├── collections/
│   │   ├── CollectionCard.jsx
│   │   ├── CreateCollectionModal.jsx
│   │   └── CollectionList.jsx
│   ├── documents/
│   │   ├── DocumentList.jsx
│   │   ├── DocumentCard.jsx
│   │   ├── UploadDropzone.jsx
│   │   └── ProcessingStatus.jsx
│   ├── chat/
│   │   ├── ChatWindow.jsx
│   │   ├── MessageBubble.jsx
│   │   ├── CitationCard.jsx
│   │   ├── MessageInput.jsx
│   │   └── SessionList.jsx
│   └── shared/
│       ├── Button.jsx
│       ├── Badge.jsx
│       ├── Spinner.jsx
│       └── ErrorBoundary.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useChat.js
│   ├── useDocuments.js
│   └── useSSE.js              → SSE streaming hook
├── services/
│   ├── api.js                 → axios instance with auth interceptor
│   ├── authService.js
│   ├── collectionService.js
│   ├── documentService.js
│   └── chatService.js
└── store/
    └── authStore.js           → Zustand for auth state
```

### Key UI Behaviors

**Document Upload:**
- Drag and drop zone with file type validation (PDF only)
- Upload progress bar with percentage
- Processing status polling every 3 seconds until status = `ready`
- Error state with retry option

**Chat Interface:**
- Left sidebar: collection documents and session history
- Main area: conversation thread
- Each assistant message shows answer + collapsible citations
- Citations show: document name, page number, and highlighted excerpt
- Streaming text — answer appears word by word as it generates
- Input disabled while response is streaming

**Collections Dashboard:**
- Grid of collection cards showing name, document count, last updated
- Click collection → view documents and start chat session

---

## 6. RAG Pipeline Design

### Ingestion Pipeline (runs on document upload)
```
PDF Upload
    ↓
Parse PDF with PyMuPDF
    → Extract text per page
    → Preserve page numbers
    ↓
Split into chunks
    → Chunk size: 512 tokens
    → Overlap: 50 tokens
    → Strategy: paragraph-aware splitting
    ↓
Generate embeddings
    → Anthropic text embedding model
    → One API call per chunk (batched)
    ↓
Store in PostgreSQL
    → document_chunks table (text + metadata)
    → chunk_embeddings table (pgvector)
    ↓
Update document status → ready
```

### Query Pipeline (runs on each user message)
```
User Query
    ↓
Embed query
    → Same embedding model as ingestion
    ↓
Vector search (pgvector)
    → Cosine similarity against collection's chunk embeddings
    → Retrieve top 10 candidates
    ↓
Rerank
    → Score by relevance, filter below threshold
    → Keep top 5 chunks
    ↓
Build prompt
    → System: "Answer using only the provided context. Cite sources."
    → Context: top 5 chunks with document name and page number
    → History: last 6 messages for conversational context
    → User query
    ↓
Call Claude API (streaming)
    → Stream answer back to FE via SSE
    ↓
Extract citations
    → Parse which chunks were referenced
    → Return citation metadata with answer
    ↓
Log to query_logs
    → Tokens used, cost, latency
```

### Prompt Template
```
System:
You are a document assistant. Answer questions using ONLY the context provided below.
Always cite the source document and page number for every claim.
If the answer is not in the context, say "I couldn't find that in the uploaded documents."

Context:
[1] Document: contract.pdf | Page: 3
"The agreement may be terminated by either party with 30 days written notice..."

[2] Document: contract.pdf | Page: 7
"Termination for cause requires written notification within 5 business days..."

Conversation History:
User: What is the contract start date?
Assistant: The contract starts on January 1, 2026 [1].

Current Question:
{user_query}
```

---

## 7. Coding Standards

### Python / FastAPI

**Folder naming:** snake_case  
**File naming:** snake_case.py  
**Class naming:** PascalCase  
**Function naming:** snake_case  

**Every route must:**
- Use Pydantic models for request and response
- Return consistent error structure
- Log request and response at DEBUG level
- Handle exceptions with try/catch, never let unhandled exceptions reach the user

**Service layer pattern:**
```python
# routes only handle HTTP concerns
@router.post("/collections", response_model=CollectionResponse)
async def create_collection(
    body: CreateCollectionRequest,
    current_user: User = Depends(get_current_user),
    service: CollectionService = Depends()
):
    return await service.create(user_id=current_user.id, data=body)

# all business logic lives in services
class CollectionService:
    async def create(self, user_id: UUID, data: CreateCollectionRequest) -> Collection:
        ...
```

**Error handling:**
```python
# Custom exception classes
class DocumentNotFoundError(AppException):
    code = "DOCUMENT_NOT_FOUND"
    status_code = 404

# Global exception handler in main.py
@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": str(exc)}}
    )
```

**Logging:**
```python
import structlog
logger = structlog.get_logger()

# Always include context
logger.info("document.ingestion.started", document_id=str(doc.id), filename=doc.filename)
logger.error("document.ingestion.failed", document_id=str(doc.id), error=str(e))
```

### React / Frontend

**Component naming:** PascalCase  
**File naming:** PascalCase.jsx for components, camelCase.js for hooks/services  
**No inline styles** — TailwindCSS classes only  
**No prop drilling beyond 2 levels** — use React Query or Zustand  

**API calls always go through service layer:**
```javascript
// Never call axios directly from components
// Always use service functions
const { data, isLoading } = useQuery({
  queryKey: ['collection', id],
  queryFn: () => collectionService.getById(id)
});
```

---

## 8. Integration Points

### Frontend → Backend
- All requests go through `src/services/api.js` (axios instance)
- JWT token auto-attached via request interceptor
- 401 responses trigger logout via response interceptor
- SSE streaming handled by `useSSE.js` hook using `EventSource` API

### Backend → Database
- SQLAlchemy async sessions via `AsyncSession`
- All DB operations in repository classes
- Alembic for all schema changes — no manual SQL in production

### Backend → Anthropic API
- Single `AnthropicService` class wraps all Claude API calls
- Tracks tokens in and out for every call
- Calculates cost and writes to `query_logs`
- Retries on rate limit (exponential backoff, max 3 retries)

### Backend → pgvector
- pgvector extension enabled on PostgreSQL
- IVFFlat index on `chunk_embeddings.embedding` for fast ANN search
- Cosine similarity: `embedding <=> query_embedding`

---

## 9. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Query response time | < 3 seconds end to end |
| Document ingestion | < 60 seconds for 100-page PDF |
| Max PDF size | 50MB |
| Max pages per PDF | 200 pages |
| API uptime | 99% (Railway SLA) |
| Auth token expiry | 24 hours |
| Cost per query | Tracked, target < $0.01 average |

### Security
- Passwords hashed with bcrypt (min cost factor 12)
- JWT signed with RS256
- Users can only access their own collections, documents, and sessions
- File uploads validated — PDF MIME type only, size limit enforced
- Environment variables for all secrets — never hardcoded

---

## 10. Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@host/novamind
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET_KEY=...
JWT_ALGORITHM=RS256
JWT_EXPIRY_HOURS=24
MAX_UPLOAD_SIZE_MB=50
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=50
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
ENVIRONMENT=development

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 11. Local Development Setup

```bash
# Clone and start everything
git clone https://github.com/jigargajjar/novamind-ai
cd novamind-ai
docker-compose up

# Services
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs   → Swagger auto-generated
Database:  localhost:5432
```

**docker-compose.yml services:**
- `db` — PostgreSQL 15 with pgvector extension
- `api` — FastAPI with hot reload
- `web` — React with Vite dev server

---

## 12. Deployment Plan

### Frontend → Vercel
- Connect GitHub repo
- Auto deploy on push to `main`
- Set `VITE_API_BASE_URL` in Vercel environment variables

### Backend + DB → Railway
- Deploy FastAPI service from GitHub
- Provision PostgreSQL plugin (pgvector pre-installed)
- Set all environment variables in Railway dashboard
- Run `alembic upgrade head` on first deploy via start command

### CI/CD (GitHub Actions)
```yaml
on: push to main
jobs:
  - lint (ruff for Python, eslint for React)
  - test (pytest for backend, vitest for frontend)
  - deploy (trigger Vercel + Railway deploys)
```

---

## 13. Project Folder Structure

```
novamind-ai/
├── PRD.md                          → this file
├── CLAUDE.md                       → Claude Code project context
├── README.md                       → public documentation
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   │   └── versions/
│   └── src/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── services/
│   │   ├── models/
│   │   └── db/
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
    │   ├── pages/
    │   ├── components/
    │   ├── hooks/
    │   ├── services/
    │   └── store/
    └── tests/
```

---

## 14. Build Order

Follow this sequence to avoid blockers:

```
Week 1 — Foundation
  → Repo setup, Docker Compose, PostgreSQL + pgvector running
  → FastAPI skeleton with auth (register, login, JWT)
  → Alembic migrations for all tables
  → React app scaffold with routing and auth pages

Week 2 — Core Pipeline
  → PDF upload endpoint + PyMuPDF parsing
  → Chunking + embedding generation
  → pgvector storage and cosine similarity search
  → Collections and documents CRUD

Week 3 — RAG + Chat
  → Full RAG query pipeline
  → Claude API integration with streaming
  → SSE streaming to frontend
  → Chat session and message storage
  → Citation extraction and storage

Week 4 — Polish + Deploy
  → Frontend chat UI with streaming and citations
  → Cost tracking and admin panel
  → Error handling, logging, edge cases
  → Deploy to Vercel + Railway
  → README with architecture diagram and demo GIF
```
