import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatRequest {
  message: string;
  agent_id?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  response: string;
  agent_id: string;
  model?: string;
  usage?: {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
  };
}

export interface RAGIngestRequest {
  text: string;
  document_id?: string;
  metadata?: Record<string, any>;
  chunk?: boolean;
}

export interface MCPExecuteRequest {
  tool_name: string;
  parameters: Record<string, any>;
}

export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },

  listAgents: async () => {
    const response = await api.get('/agents');
    return response.data;
  },
};

export const ragApi = {
  ingest: async (request: RAGIngestRequest) => {
    const response = await api.post('/rag/ingest', request);
    return response.data;
  },

  search: async (query: string, topK: number = 5) => {
    const response = await api.get('/rag/search', {
      params: { query, top_k: topK },
    });
    return response.data;
  },
};

export const mcpApi = {
  listTools: async () => {
    const response = await api.get('/mcp/tools');
    return response.data;
  },

  executeTool: async (request: MCPExecuteRequest) => {
    const response = await api.post('/mcp/execute', request);
    return response.data;
  },
};

export const voiceApi = {
  initiateCall: async (phoneNumber: string, assistantId?: string) => {
    const response = await api.post('/voice/call', {
      phone_number: phoneNumber,
      assistant_id: assistantId,
    });
    return response.data;
  },
};

