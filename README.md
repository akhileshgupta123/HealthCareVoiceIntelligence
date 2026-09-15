# Real-Time Healthcare Operations Assistant

A voice-first, AI-driven platform designed to streamline clinical and administrative workflows using Moss for sub-10ms context retrieval.

## Architecture

This project implements a multi-agent voice copilot for healthcare operations:

- **Frontend Layer**: React/TypeScript with Next.js and LiveKit SDK for WebRTC audio
- **Voice Layer**: LiveKit for STT/TTS/VAD with full-duplex audio streaming
- **AI Agent Layer**: LangGraph-based multi-agent system (Supervisor, Claims, Knowledge, Escalation)
- **Data Layer**: Moss for sub-10ms semantic search, FastAPI mock APIs, SQLite database

## Components

### Backend (Python)
- FastAPI web framework
- LangGraph for agent orchestration
- Moss SDK for semantic search
- SQLAlchemy with SQLite (POC) / PostgreSQL (production)
- LiveKit agent integration

### Frontend (React/TypeScript)
- Next.js framework
- LiveKit SDK for voice
- Tailwind CSS for styling
- Real-time voice interface

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, LangGraph, Moss SDK, SQLAlchemy
- **Frontend**: Node.js 20+, React, Next.js, TypeScript, LiveKit SDK
- **Database**: SQLite (POC), PostgreSQL (production)
- **Voice**: LiveKit WebRTC

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 20+

### Setup

1. Clone the repository
2. Copy environment files:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

3. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

5. Start the backend:
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Start the frontend (new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

7. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
moss/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── moss_client.py       # Moss SDK integration
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   └── routers/             # API endpoints
│   │       ├── claims.py
│   │       ├── checks.py
│   │       ├── tickets.py
│   │       ├── eligibility.py
│   │       └── knowledge.py
│   ├── agents/
│   │   ├── supervisor.py        # LangGraph supervisor agent
│   │   ├── workers.py           # Worker agents
│   │   └── livekit_agent.py     # LiveKit integration
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main page
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   └── VoiceAssistant.tsx   # LiveKit voice component
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── .env.example
├── .env.example
├── SETUP.md
└── README.md
```

## Features

- **Real-time Voice Interaction**: WebRTC-based full-duplex audio
- **Multi-Agent System**: Specialized agents for claims, knowledge, and escalation
- **Sub-10ms Context Retrieval**: Moss-powered semantic search
- **HIPAA Compliance**: Security and privacy features
- **Mock Healthcare APIs**: Claims, checks, tickets, eligibility endpoints

## API Endpoints

### Claims
- `GET /api/v1/claims/{id}` - Get claim details
- `GET /api/v1/claims` - List all claims

### Checks
- `GET /api/v1/checks/{id}` - Get check details
- `GET /api/v1/checks` - List all checks

### Tickets
- `POST /api/v1/tickets` - Create escalation ticket
- `GET /api/v1/tickets/{id}` - Get ticket details
- `GET /api/v1/tickets` - List all tickets
- `PUT /api/v1/tickets/{id}` - Update ticket

### Eligibility
- `GET /api/v1/eligibility/{patient_id}` - Get patient eligibility
- `GET /api/v1/eligibility` - List all eligibility records

### Knowledge
- `POST /api/v1/knowledge/search` - Search knowledge base

## Environment Variables

See `.env.example` for required environment variables:
- Moss credentials (PROJECT_ID, PROJECT_KEY)
- Database URL (SQLite by default)
- LiveKit credentials
- LLM API keys

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## License

MIT
