"""MCP server implementation."""

from typing import Dict, Any, List, Optional
from app.mcp.tools import MCPToolRegistry
from app.utils.logger import logger


class MCPServer:
    """MCP server for tool integration."""

    def __init__(self):
        """Initialize MCP server."""
        self.tool_registry = MCPToolRegistry()
        logger.info("Initialized MCP server")

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools.

        Returns:
            List of tool schemas
        """
        return self.tool_registry.list_tools()

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        logger.info(f"Executing MCP tool: {tool_name}")
        result = await self.tool_registry.execute_tool(tool_name, parameters)
        return result

    async def execute_tools(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tools.

        Args:
            tool_calls: List of tool call dictionaries

        Returns:
            List of tool execution results
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name")
            if not tool_name:
                continue

            # Extract parameters
            if "arguments" in tool_call:
                import json
                if isinstance(tool_call["arguments"], str):
                    parameters = json.loads(tool_call["arguments"])
                else:
                    parameters = tool_call["arguments"]
            elif "input" in tool_call:
                parameters = tool_call["input"]
            else:
                parameters = tool_call.get("parameters", {})

            result = await self.execute_tool(tool_name, parameters)
            results.append(result)

        return results

