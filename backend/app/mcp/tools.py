"""MCP tool definitions and implementations."""

from typing import Any, Dict, List, Optional
import json
import httpx
import os
from app.utils.logger import logger
from app.utils.helpers import format_tool_output


class MCPTool:
    """Base class for MCP tools."""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        """
        Initialize MCP tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON Schema parameters definition
        """
        self.name = name
        self.description = description
        self.parameters = parameters

    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for LLM.

        Returns:
            Tool schema dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        raise NotImplementedError("Subclasses must implement execute method")


class WebSearchTool(MCPTool):
    """Tool for web search (placeholder - requires search API)."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )

    async def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute web search.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            Search results
        """
        try:
            # Placeholder implementation - would integrate with search API
            logger.info(f"Web search: {query}")
            return format_tool_output(
                self.name,
                {
                    "query": query,
                    "results": [
                        {
                            "title": f"Result {i+1} for {query}",
                            "url": f"https://example.com/result{i+1}",
                            "snippet": f"Sample result snippet {i+1}"
                        }
                        for i in range(max_results)
                    ]
                }
            )
        except Exception as e:
            return format_tool_output(self.name, None, str(e))


class CalculatorTool(MCPTool):
    """Tool for mathematical calculations."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        )

    async def execute(self, expression: str) -> Dict[str, Any]:
        """
        Execute calculation.

        Args:
            expression: Mathematical expression

        Returns:
            Calculation result
        """
        try:
            # Safe evaluation of mathematical expressions
            allowed_chars = set("0123456789+-*/()., ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")

            result = eval(expression)
            return format_tool_output(self.name, {"expression": expression, "result": result})
        except Exception as e:
            return format_tool_output(self.name, None, str(e))


class FileReadTool(MCPTool):
    """Tool for reading files."""

    def __init__(self, base_path: str = "./data"):
        super().__init__(
            name="file_read",
            description="Read contents of a file",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file relative to base directory"
                    }
                },
                "required": ["file_path"]
            }
        )
        self.base_path = base_path

    async def execute(self, file_path: str) -> Dict[str, Any]:
        """
        Read file contents.

        Args:
            file_path: File path relative to base

        Returns:
            File contents
        """
        try:
            # Security: prevent path traversal
            full_path = os.path.join(self.base_path, file_path)
            if not os.path.abspath(full_path).startswith(os.path.abspath(self.base_path)):
                raise ValueError("Invalid file path")

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            return format_tool_output(
                self.name,
                {
                    "file_path": file_path,
                    "content": content,
                    "size": len(content)
                }
            )
        except Exception as e:
            return format_tool_output(self.name, None, str(e))


class APICallTool(MCPTool):
    """Tool for making HTTP API calls."""

    def __init__(self):
        super().__init__(
            name="api_call",
            description="Make HTTP API call",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "API endpoint URL"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers"
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body"
                    }
                },
                "required": ["url"]
            }
        )

    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute API call.

        Args:
            url: API URL
            method: HTTP method
            headers: HTTP headers
            body: Request body

        Returns:
            API response
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    json=body
                )
                response.raise_for_status()

                return format_tool_output(
                    self.name,
                    {
                        "url": url,
                        "method": method,
                        "status_code": response.status_code,
                        "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    }
                )
        except Exception as e:
            return format_tool_output(self.name, None, str(e))


class DatabaseQueryTool(MCPTool):
    """Tool for database queries (placeholder)."""

    def __init__(self):
        super().__init__(
            name="database_query",
            description="Execute database query",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query"
                    }
                },
                "required": ["query"]
            }
        )

    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute database query.

        Args:
            query: SQL query

        Returns:
            Query results
        """
        try:
            # Placeholder - would integrate with actual database
            logger.info(f"Database query: {query}")
            return format_tool_output(
                self.name,
                {
                    "query": query,
                    "results": [],
                    "row_count": 0
                }
            )
        except Exception as e:
            return format_tool_output(self.name, None, str(e))


class MCPToolRegistry:
    """Registry for MCP tools."""

    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools."""
        self.register(WebSearchTool())
        self.register(CalculatorTool())
        self.register(FileReadTool())
        self.register(APICallTool())
        self.register(DatabaseQueryTool())

    def register(self, tool: MCPTool):
        """
        Register a tool.

        Args:
            tool: Tool instance
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """
        Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools.

        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]

    async def execute_tool(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool.

        Args:
            name: Tool name
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            return format_tool_output(name, None, f"Tool '{name}' not found")

        try:
            return await tool.execute(**parameters)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
            return format_tool_output(name, None, str(e))

