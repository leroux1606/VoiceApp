import React, { useState, useEffect } from 'react';
import { Activity, Database, Wrench, MessageSquare } from 'lucide-react';
import { chatApi, ragApi, mcpApi } from '../services/api';

export function AgentDashboard() {
  const [agents, setAgents] = useState<any[]>([]);
  const [ragQuery, setRagQuery] = useState('');
  const [ragResults, setRagResults] = useState<any[]>([]);
  const [mcpTools, setMcpTools] = useState<any[]>([]);
  const [selectedTool, setSelectedTool] = useState<string>('');
  const [toolParams, setToolParams] = useState<Record<string, any>>({});
  const [toolResult, setToolResult] = useState<any>(null);

  useEffect(() => {
    loadAgents();
    loadMCPTools();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await chatApi.listAgents();
      setAgents(response.agents || []);
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const loadMCPTools = async () => {
    try {
      const response = await mcpApi.listTools();
      setMcpTools(response.tools || []);
    } catch (error) {
      console.error('Error loading MCP tools:', error);
    }
  };

  const handleRAGSearch = async () => {
    if (!ragQuery.trim()) return;
    try {
      const response = await ragApi.search(ragQuery, 5);
      setRagResults(response.results || []);
    } catch (error) {
      console.error('Error searching RAG:', error);
    }
  };

  const handleToolExecute = async () => {
    if (!selectedTool) return;
    try {
      const response = await mcpApi.executeTool({
        tool_name: selectedTool,
        parameters: toolParams,
      });
      setToolResult(response);
    } catch (error) {
      console.error('Error executing tool:', error);
    }
  };

  return (
    <div className="dashboard p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-6">Agent Dashboard</h1>

      {/* Agents Status */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Activity size={24} />
          <h2 className="text-xl font-semibold">Active Agents</h2>
        </div>
        <div className="space-y-2">
          {agents.length === 0 ? (
            <p className="text-gray-500">No active agents</p>
          ) : (
            agents.map((agent) => (
              <div key={agent.id} className="border rounded p-3">
                <div className="flex justify-between">
                  <span className="font-medium">{agent.id}</span>
                  <span className="text-sm text-gray-500">{agent.type}</span>
                </div>
                {agent.stats && (
                  <div className="text-sm text-gray-600 mt-2">
                    <p>Messages: {agent.stats.message_count}</p>
                    <p>Tokens: {agent.stats.total_tokens_used}</p>
                    <p>Cost: ${agent.stats.total_cost.toFixed(4)}</p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* RAG Search */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Database size={24} />
          <h2 className="text-xl font-semibold">RAG Knowledge Base</h2>
        </div>
        <div className="flex space-x-2 mb-4">
          <input
            type="text"
            value={ragQuery}
            onChange={(e) => setRagQuery(e.target.value)}
            placeholder="Search knowledge base..."
            className="flex-1 border rounded p-2"
            onKeyPress={(e) => e.key === 'Enter' && handleRAGSearch()}
          />
          <button
            onClick={handleRAGSearch}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Search
          </button>
        </div>
        <div className="space-y-2">
          {ragResults.map((result, index) => (
            <div key={index} className="border rounded p-3">
              <p className="text-sm text-gray-600 mb-2">Score: {result.score?.toFixed(3)}</p>
              <p className="text-sm">{result.document}</p>
            </div>
          ))}
        </div>
      </div>

      {/* MCP Tools */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Wrench size={24} />
          <h2 className="text-xl font-semibold">MCP Tools</h2>
        </div>
        <div className="space-y-4">
          <select
            value={selectedTool}
            onChange={(e) => setSelectedTool(e.target.value)}
            className="w-full border rounded p-2"
          >
            <option value="">Select a tool</option>
            {mcpTools.map((tool) => (
              <option key={tool.name} value={tool.name}>
                {tool.name} - {tool.description}
              </option>
            ))}
          </select>

          {selectedTool && (
            <>
              <div className="space-y-2">
                {mcpTools
                  .find((t) => t.name === selectedTool)
                  ?.input_schema?.properties &&
                  Object.entries(
                    mcpTools.find((t) => t.name === selectedTool)!.input_schema.properties
                  ).map(([key, schema]: [string, any]) => (
                    <div key={key}>
                      <label className="block text-sm font-medium mb-1">{key}</label>
                      <input
                        type="text"
                        value={toolParams[key] || ''}
                        onChange={(e) =>
                          setToolParams({ ...toolParams, [key]: e.target.value })
                        }
                        placeholder={schema.description}
                        className="w-full border rounded p-2"
                      />
                    </div>
                  ))}
              </div>
              <button
                onClick={handleToolExecute}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Execute Tool
              </button>
            </>
          )}

          {toolResult && (
            <div className="mt-4 border rounded p-3 bg-gray-50">
              <pre className="text-sm overflow-auto">
                {JSON.stringify(toolResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

