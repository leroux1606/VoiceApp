# AI Agent System

A comprehensive AI agent system with voice capabilities, LLM integration, RAG (Retrieval-Augmented Generation), MCP (Model Context Protocol), and real-time communication.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   FastAPI    │────────▶│    LLMs    │
│   (React)   │         │   Backend    │         │ Claude/OpenAI│
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ├────────▶ ChromaDB (Vector Store)
                              │
                              ├────────▶ LiveKit (WebRTC)
                              │
                              ├────────▶ ElevenLabs (TTS)
                              │
                              └────────▶ MCP Tools
```

## Features

- **Multi-LLM Support**: Claude and OpenAI integration with automatic fallback
- **Voice Interface**: WebRTC-based voice communication with LiveKit
- **RAG System**: Document ingestion and semantic search with ChromaDB
- **MCP Tools**: Extensible tool system for function calling
- **Real-time Chat**: WebSocket-based real-time communication
- **Agent Management**: Multiple agent instances with conversation history
- **Modern UI**: React + TypeScript frontend with Tailwind CSS

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional)
- API keys for:
  - Anthropic (Claude)
  - OpenAI (optional)
  - ElevenLabs (for TTS)
  - Vapi (for voice calls)
  - LiveKit (for WebRTC)

## Quick Start

### Using Docker Compose

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-agent-system
```

2. Copy environment file:
```bash
cp backend/.env.example backend/.env
```

3. Edit `backend/.env` and add your API keys.

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ChromaDB: http://localhost:8001
- n8n: http://localhost:5678

### Manual Setup

#### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Start ChromaDB (if not using Docker):
```bash
docker run -p 8000:8000 chromadb/chroma:latest
```

6. Run the backend:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

## API Documentation

### Endpoints

#### Chat
- `POST /api/chat` - Send a chat message
- `GET /api/agents` - List all agents

#### RAG
- `POST /api/rag/ingest` - Ingest a document
- `GET /api/rag/search` - Search knowledge base

#### MCP Tools
- `GET /api/mcp/tools` - List available tools
- `POST /api/mcp/execute` - Execute a tool

#### Voice
- `POST /api/voice/call` - Initiate voice call

#### WebSocket
- `WS /api/ws/{client_id}` - Real-time chat connection

### Example API Calls

#### Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "agent_id": "chat_agent",
    "temperature": 0.7
  }'
```

#### RAG Ingestion
```bash
curl -X POST http://localhost:8000/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a sample document for the knowledge base.",
    "metadata": {"title": "Sample Document"},
    "chunk": true
  }'
```

#### RAG Search
```bash
curl "http://localhost:8000/api/rag/search?query=sample&top_k=5"
```

#### MCP Tool Execution
```bash
curl -X POST http://localhost:8000/api/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculator",
    "parameters": {"expression": "2 + 2"}
  }'
```

## Configuration

### Environment Variables

See `backend/.env.example` for all available configuration options.

Key settings:
- `ANTHROPIC_API_KEY` - Required for Claude
- `OPENAI_API_KEY` - Required for OpenAI
- `ELEVENLABS_API_KEY` - Required for TTS
- `CHROMA_HOST` - ChromaDB host (default: localhost)
- `CHROMA_PORT` - ChromaDB port (default: 8000)

## Project Structure

```
ai-agent-system/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── agents/       # Agent implementations
│   │   ├── llm/          # LLM clients
│   │   ├── rag/          # RAG system
│   │   ├── voice/        # Voice integrations
│   │   ├── mcp/          # MCP tools
│   │   └── api/          # API routes
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   └── services/     # API services
│   └── package.json
├── tests/                # Test files
└── docker-compose.yml    # Docker configuration
```

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Quality

- Type hints throughout Python code
- ESLint for TypeScript/React
- Pydantic models for validation
- Structured logging

## Deployment

### Production Considerations

1. Set `APP_ENV=production` in environment
2. Use strong `SECRET_KEY`
3. Configure proper CORS origins
4. Set up reverse proxy (nginx)
5. Use production-grade database
6. Enable rate limiting
7. Set up monitoring and logging
8. Use HTTPS for all connections

## Troubleshooting

### ChromaDB Connection Issues

If ChromaDB connection fails, ensure:
- ChromaDB is running on configured host/port
- Network connectivity is available
- Firewall allows connections

### LLM API Errors

- Verify API keys are correct
- Check API rate limits
- Ensure sufficient API credits

### WebSocket Issues

- Check CORS configuration
- Verify WebSocket URL is correct
- Check firewall settings

## License

[Your License Here]

## Contributing

[Contributing Guidelines]

## Support

[Support Information]

