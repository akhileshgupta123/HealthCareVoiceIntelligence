# Healthcare Operations Assistant - Setup Guide

This guide will help you set up and run the Real-Time Healthcare Operations Assistant with Moss integration.

## Prerequisites

- **Python 3.10+**
- **Node.js 20+**
- **Git**

**Note**: SQLite is used by default (no database setup required). For production, PostgreSQL can be configured.

## Quick Start

### 1. Clone and Navigate

```bash
cd c:\moss
```

### 2. Environment Configuration

Copy the example environment files and configure them:

```bash
# Root environment
cp .env.example .env

# Backend environment
cd backend
cp .env.example .env
cd ..

# Frontend environment
cd frontend
cp .env.example .env.local
cd ..
```

### 3. Configure Required Environment Variables

Edit the `.env` files with your actual credentials:

**Root `.env`:**
```env
MOSS_PROJECT_ID=a4e255d3-be54-4ce1-aae0-d249f7663da4
MOSS_PROJECT_KEY=moss_328e6205290b996520ca702c99dbcb96
DATABASE_URL=sqlite:///./healthcare_ops.db  # SQLite for POC
OPENAI_API_KEY=your_openai_api_key
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=ws://localhost:7880
```

**Backend `.env`:**
```env
MOSS_PROJECT_ID=a4e255d3-be54-4ce1-aae0-d249f7663da4
MOSS_PROJECT_KEY=moss_328e6205290b996520ca702c99dbcb96
DATABASE_URL=sqlite:///./healthcare_ops.db  # SQLite for POC
OPENAI_API_KEY=your_openai_api_key
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=ws://localhost:7880
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
NEXT_PUBLIC_LIVEKIT_TOKEN=your_livekit_token
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Install Python Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
cd ..
```

### 5. Install Node.js Dependencies

```bash
cd frontend
npm install
cd ..
```

### 6. Start the Backend Server

```bash
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 7. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Verify Installation

### Test Backend API

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Healthcare Operations Assistant API",
  "version": "1.0.0",
  "status": "operational"
}
```

### Test API Endpoints

```bash
# Get claim status
curl http://localhost:8000/api/v1/claims/CLM001

# Get check status
curl http://localhost:8000/api/v1/checks/CHK001

# Check eligibility
curl http://localhost:8000/api/v1/eligibility/PAT001

# Search knowledge base
curl -X POST http://localhost:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "claim submission process", "top_k": 3}'
```

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
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main page
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   └── VoiceAssistant.tsx   # LiveKit voice component
│   ├── package.json
│   ├── Dockerfile
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── .env.example
├── docker-compose.yml
├── .env.example
└── README.md
```

## Architecture Overview

### Frontend Layer
- **React/TypeScript** with Next.js
- **LiveKit SDK** for WebRTC audio
- Real-time voice interface

### Voice Layer
- **LiveKit** for STT/TTS/VAD
- Full-duplex audio streaming

### AI Agent Layer
- **Supervisor Agent** (LangGraph) - Routes requests
- **Claims Agent** - Handles claim/payment queries
- **Knowledge Agent** - Retrieves policy information
- **Escalation Agent** - Creates support tickets

### Data Layer
- **Moss** - Sub-10ms semantic search for context and knowledge
- **FastAPI** - Mock healthcare APIs
- **PostgreSQL** - Persistent data storage

## Moss Integration

The system uses Moss for:

1. **Session Context Index** - Stores conversation history for real-time context
2. **Knowledge Base Index** - Indexed policies and procedures for instant retrieval

Moss provides sub-10ms retrieval latency, enabling real-time voice interactions.

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Change port in the uvicorn command
python -m uvicorn api.main:app --reload --port 8001
```

**Database connection error:**
```bash
# For SQLite: Check that the database file exists in the backend directory
ls backend/healthcare_ops.db
```

### Frontend Issues

**TypeScript errors after npm install:**
- These are expected during development and will resolve once dependencies are installed
- Run `npm install` again if issues persist

**Port 3000 already in use:**
```bash
# Change port in package.json
"dev": "next dev -p 3001"
```

### Moss Connection Issues

**Invalid credentials:**
- Verify MOSS_PROJECT_ID and MOSS_PROJECT_KEY in `.env` files
- Check that credentials match your Moss project

**Index not found:**
- The system will auto-create indexes on first run
- Check backend logs for initialization status

## Development

### Adding New Knowledge Base Documents

Edit `backend/api/moss_client.py` and add documents to the `_index_sample_knowledge` method:

```python
{
    "id": "kb_006",
    "text": "Your new knowledge content here",
    "metadata": {"category": "your_category", "priority": "high"}
}
```

### Adding New API Endpoints

1. Create a new router in `backend/api/routers/`
2. Register it in `backend/api/main.py`
3. Add corresponding models in `backend/api/models.py`

### Adding New Worker Agents

1. Create a new agent class in `backend/agents/workers.py`
2. Add routing logic in `backend/agents/supervisor.py`
3. Update the LangGraph workflow

## Security Considerations

For production deployment:

1. **Environment Variables**: Never commit `.env` files
2. **HIPAA Compliance**: Ensure all PHI is encrypted
3. **Authentication**: Implement OAuth2/JWT as specified in PRD
4. **Audit Logging**: Enable comprehensive logging
5. **HTTPS**: Use SSL/TLS for all communications

## Next Steps

1. Configure LiveKit server for voice functionality
2. Set up OpenAI API key for LLM functionality
3. Test the complete voice pipeline
4. Implement authentication/authorization
5. Add observability (OpenSearch, Grafana)
6. Deploy to Kubernetes (EKS)

## Support

For issues or questions:
- Check the PRD document for detailed requirements
- Review the architecture diagram for system design
- Consult Moss documentation at https://docs.moss.dev
