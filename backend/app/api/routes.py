"""FastAPI routes for the application."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from app.agents.chat_agent import ChatAgent
from app.agents.voice_agent import VoiceAgent
from app.rag.vectorstore import VectorStore
from app.rag.retriever import RAGRetriever
from app.mcp.server import MCPServer
from app.voice.vapi_client import VapiClient
from app.utils.logger import logger

router = APIRouter()

# Agent instances (in production, use dependency injection)
_agents: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(..., description="User message")
    agent_id: Optional[str] = Field(default="chat_agent", description="Agent ID")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=4096)


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str
    agent_id: str
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


class VoiceCallRequest(BaseModel):
    """Voice call request model."""

    phone_number: str = Field(..., description="Phone number to call")
    assistant_id: Optional[str] = None
    assistant_config: Optional[Dict[str, Any]] = None


class RAGIngestRequest(BaseModel):
    """RAG document ingestion request."""

    text: str = Field(..., description="Document text")
    document_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    chunk: Optional[bool] = Field(default=False, description="Whether to chunk the document")


class RAGSearchRequest(BaseModel):
    """RAG search request."""

    query: str = Field(..., description="Search query")
    top_k: Optional[int] = Field(default=5, ge=1, le=20)


class MCPExecuteRequest(BaseModel):
    """MCP tool execution request."""

    tool_name: str = Field(..., description="Tool name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


def get_agent(agent_id: str = "chat_agent") -> ChatAgent:
    """
    Get or create agent instance.

    Args:
        agent_id: Agent ID

    Returns:
        Agent instance
    """
    if agent_id not in _agents:
        if agent_id == "voice_agent":
            _agents[agent_id] = VoiceAgent(agent_id=agent_id)
        else:
            _agents[agent_id] = ChatAgent(agent_id=agent_id)
    return _agents[agent_id]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Text-based chat endpoint.

    Args:
        request: Chat request

    Returns:
        Chat response
    """
    try:
        agent = get_agent(request.agent_id)
        result = await agent.process(
            request.message,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            response=result["response"],
            agent_id=result["agent_id"],
            model=result.get("model"),
            usage=result.get("usage")
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/call")
async def initiate_voice_call(request: VoiceCallRequest):
    """
    Initiate a voice call using Vapi.

    Args:
        request: Voice call request

    Returns:
        Call creation response
    """
    try:
        vapi_client = VapiClient()
        result = await vapi_client.create_call(
            phone_number=request.phone_number,
            assistant_id=request.assistant_id,
            assistant_config=request.assistant_config
        )
        await vapi_client.close()
        return result
    except Exception as e:
        logger.error(f"Error initiating voice call: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """
    List all available agents.

    Returns:
        List of agent information
    """
    agents_info = []
    for agent_id, agent in _agents.items():
        agents_info.append({
            "id": agent_id,
            "type": type(agent).__name__,
            "stats": agent.get_stats()
        })
    return {"agents": agents_info}


@router.post("/rag/ingest")
async def ingest_document(request: RAGIngestRequest):
    """
    Ingest a document into the RAG system.

    Args:
        request: Document ingestion request

    Returns:
        Ingestion result
    """
    try:
        vector_store = VectorStore()
        if request.chunk:
            doc_ids = vector_store.add_document_chunked(
                text=request.text,
                document_id=request.document_id,
                metadata=request.metadata
            )
            return {
                "success": True,
                "document_ids": doc_ids,
                "chunked": True
            }
        else:
            doc_id = vector_store.add_document(
                text=request.text,
                document_id=request.document_id,
                metadata=request.metadata
            )
            return {
                "success": True,
                "document_id": doc_id,
                "chunked": False
            }
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/search")
async def search_rag(query: str, top_k: int = 5):
    """
    Search the RAG knowledge base.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        Search results
    """
    try:
        retriever = RAGRetriever()
        results = retriever.retrieve(query=query, top_k=top_k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching RAG: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/execute")
async def execute_mcp_tool(request: MCPExecuteRequest):
    """
    Execute an MCP tool.

    Args:
        request: Tool execution request

    Returns:
        Tool execution result
    """
    try:
        mcp_server = MCPServer()
        result = await mcp_server.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        return result
    except Exception as e:
        logger.error(f"Error executing MCP tool: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/tools")
async def list_mcp_tools():
    """
    List all available MCP tools.

    Returns:
        List of tool schemas
    """
    try:
        mcp_server = MCPServer()
        tools = mcp_server.get_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error listing MCP tools: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

