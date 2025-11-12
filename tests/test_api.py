"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_list_agents():
    """Test list agents endpoint."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert "agents" in response.json()


def test_list_mcp_tools():
    """Test list MCP tools endpoint."""
    response = client.get("/api/mcp/tools")
    assert response.status_code == 200
    assert "tools" in response.json()

