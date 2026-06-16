# NovaMind AI

AI-powered document intelligence platform. Upload PDF documents, organize them into collections, and ask natural language questions. The system retrieves relevant passages using semantic search and returns accurate, cited answers via a streaming RAG pipeline.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+pgvector-4169E1?logo=postgresql&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-claude--sonnet--4--6-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

---

## Features

- **PDF ingestion** — PyMuPDF extraction, paragraph-aware chunking (512 tokens / 50 overlap), async background processing
- **Semantic search** — Voyage AI `voyage-3` embeddings stored in pgvector with HNSW index
- **Reranking** — Voyage AI `rerank-2-lite` for precision over the top-10 vector candidates
- **Streaming answers** — Claude `claude-sonnet-4-6` via SSE, tokens stream to the UI in real time
- **Citations** — Claude's `[N]` references mapped back to source documents and page numbers
- **Cost tracking** — Every query logs input/output tokens, USD cost, and latency to `query_logs`
- **Collections** — Organize documents into named scopes; each chat session is scoped to one collection
- **Admin panel** — Usage stats, per-user cost breakdown, recent query log

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│  React + Zustand + React Query + Fetch SSE                 │
└────────────────────────┬────────────────────────────────────┘
                         │ REST / SSE  (JWT Bearer)
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI  (Python 3.11)                    │
│                                                             │
│  routes/           ← HTTP only, delegates to services       │
│  services/         ← business logic (ingestion, RAG, chat)  │
│  repositories/     ← SQLAlchemy async queries               │
└───────┬──────────────────────────┬──────────────────────────┘
        │                          │
┌───────▼──────────┐    ┌──────────▼──────────────────────────┐
│  PostgreSQL 15   │    │         External AI APIs             │
│  + pgvector      │    │                                      │
│                  │    │  Voyage AI — embeddings + reranking  │
│  • users         │    │  Anthropic — Claude streaming chat   │
│  • collections   │    │                                      │
│  • documents     │    └─────────────────────────────────────┘
│  • document_     │
│    chunks        │
│  • chunk_        │
│    embeddings    │
│    (vector 1024) │
│  • chat_sessions │
│  • chat_messages │
│  • message_      │
│    citations     │
│  • query_logs    │
└──────────────────┘
```

### RAG Pipeline

```
User query
    │
    ▼
Voyage AI embed (query)
    │
    ▼
pgvector cosine similarity search — top 10 chunks (HNSW)
    │
    ▼
Voyage AI rerank — top 5 chunks
    │
    ▼
System prompt with numbered [N] context blocks
    │
    ▼
Claude claude-sonnet-4-6 stream → SSE → browser
    │
    ▼
Citation extraction (regex [N] → source chunk)
    │
    ▼
Persist: message, citations, query_log (tokens + cost)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| Frontend | React 18, TailwindCSS, React Query, Zustand |
| Database | PostgreSQL 15 + pgvector extension |
| Embeddings | Voyage AI `voyage-3` (1024-dim) |
| Reranking | Voyage AI `rerank-2-lite` |
| LLM | Anthropic Claude `claude-sonnet-4-6` |
| PDF parsing | PyMuPDF (fitz) |
| Auth | JWT (python-jose) |
| Containerization | Docker + Docker Compose |

---

## Local Setup

### Prerequisites

- Docker + Docker Compose
- Node.js 18+
- Anthropic API key
- Voyage AI API key

### 1. Clone and configure

```bash
git clone https://github.com/jigargajjarcad/novamind-ai.git
cd novamind-ai
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://novamind:novamind@db:5432/novamind
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=["http://localhost:3000"]
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 2. Start all services

```bash
docker compose up --build
```

This starts:
- **PostgreSQL 15** with pgvector on port `5432`
- **FastAPI** on port `8000` (hot reload enabled)
- **React** on port `3000` (Vite HMR enabled)

### 3. Run migrations

Migrations run automatically on API startup via `alembic upgrade head`.

To run manually:

```bash
docker compose exec api alembic upgrade head
```

### 4. Open the app

- **App**: http://localhost:3000
- **API docs**: http://localhost:8000/docs

---

## API Reference

### Auth
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login, receive JWT |
| `GET` | `/api/v1/auth/me` | Current user info |

### Collections
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/collections` | List all collections |
| `POST` | `/api/v1/collections` | Create collection |
| `GET` | `/api/v1/collections/{id}` | Get collection |
| `PUT` | `/api/v1/collections/{id}` | Update collection |
| `DELETE` | `/api/v1/collections/{id}` | Delete collection |

### Documents
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/collections/{id}/documents` | Upload PDF (202, async ingestion) |
| `GET` | `/api/v1/collections/{id}/documents` | List documents |
| `GET` | `/api/v1/documents/{id}` | Get document (with status) |
| `DELETE` | `/api/v1/documents/{id}` | Delete document |

### Chat
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/chat/sessions` | Create chat session |
| `GET` | `/api/v1/chat/sessions` | List sessions |
| `GET` | `/api/v1/chat/sessions/{id}` | Get session with messages |
| `DELETE` | `/api/v1/chat/sessions/{id}` | Delete session |
| `POST` | `/api/v1/chat/sessions/{id}/messages` | Send message (SSE stream) |

#### SSE event sequence on `POST /messages`:

```
event: chunk       data: {"text": "..."}          ← streaming (multiple)
event: citations   data: [{filename, page, ...}]  ← after stream ends
event: done        data: {message_id, tokens, cost_usd, latency_ms}
event: error       data: {code, message}           ← on failure
```

### Admin
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/admin/usage` | Per-user token/cost summary |
| `GET` | `/api/v1/admin/queries` | Recent query log (last 50) |

---

## Project Structure

```
novamind-ai/
├── backend/
│   ├── alembic/               # Database migrations
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_update_embedding_dimension.py
│   └── src/
│       ├── api/
│       │   ├── routes/        # HTTP handlers (chat, collections, documents, admin, auth)
│       │   └── schemas/       # Pydantic request/response models
│       ├── core/
│       │   ├── config.py      # Settings from env
│       │   ├── exceptions.py  # Custom exception classes
│       │   └── security.py    # JWT encode/decode, password hashing
│       ├── db/
│       │   ├── database.py    # SQLAlchemy async engine + session factory
│       │   └── repositories/  # Data access layer
│       ├── models/            # SQLAlchemy ORM models
│       └── services/          # Business logic
│           ├── anthropic_service.py   # Voyage AI embeddings + rerank, Claude streaming
│           ├── ingestion_service.py   # PDF parse → chunk → embed → store
│           ├── rag_service.py         # Full RAG pipeline
│           └── chat_service.py        # Session management + SSE orchestration
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── chat/          # ChatWindow, MessageBubble, CitationCard, MessageInput
│       │   ├── documents/     # DocumentList, UploadDropzone
│       │   ├── layout/        # Sidebar, PageWrapper
│       │   └── shared/        # Button, Modal, etc.
│       ├── hooks/             # useSSE, useDocuments
│       ├── pages/             # Dashboard, Collection, Chat, Admin, Login, Register
│       ├── services/          # API clients (auth, collections, documents, chat, admin)
│       └── store/             # Zustand auth store
├── docker-compose.yml
└── PRD.md
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Async PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `VOYAGE_API_KEY` | Yes | Voyage AI key for embeddings and reranking |
| `JWT_SECRET_KEY` | Yes | Secret for JWT signing (min 32 chars) |
| `JWT_ALGORITHM` | No | Default: `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Default: `10080` (7 days) |
| `CORS_ORIGINS` | No | JSON array of allowed origins |

---

## License

MIT
