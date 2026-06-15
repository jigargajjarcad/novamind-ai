# NovaMind AI — Project Context for Claude Code

## What This Project Is
AI-powered document intelligence platform. Users upload PDF documents, organize them into collections, and ask natural language questions. System retrieves relevant content and returns accurate cited answers using RAG.

## Tech Stack
- Backend: Python 3.11, FastAPI, SQLAlchemy, Alembic
- Frontend: React, TailwindCSS, React Query, Zustand
- Database: PostgreSQL 15 + pgvector extension
- AI: Anthropic Claude API (claude-sonnet-4-6), Anthropic embeddings
- PDF Parsing: PyMuPDF (fitz)
- Auth: JWT (python-jose)
- Containerization: Docker + Docker Compose
- Deployment: Vercel (frontend), Railway (backend + DB)

## Project Structure
- /backend — FastAPI application
- /frontend — React application
- /docker-compose.yml — local development setup
- /PRD.md — full product requirements document (read this for complete context)

## Coding Standards — Non-Negotiable
- Production quality always — no shortcuts
- All business logic in service layer, routes handle HTTP only
- Pydantic models for all request/response schemas
- Structured logging with structlog on every service operation
- Custom exception classes with consistent error response format
- Never hardcode secrets — always use environment variables
- SQLAlchemy async sessions only
- Alembic for all database migrations — no manual SQL changes

## Current Phase
Week 1 — Foundation
- Docker Compose setup with PostgreSQL + pgvector
- FastAPI skeleton with JWT auth
- Alembic migrations for all tables
- React app scaffold with routing and auth pages

## Architecture Decisions
- CQRS-inspired service layer pattern (routes → services → repositories)
- pgvector for vector storage (no separate vector DB needed)
- SSE for streaming chat responses to frontend
- JWT RS256 for auth
