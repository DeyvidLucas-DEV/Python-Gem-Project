import pytest
from httpx import AsyncClient
from fastapi import status

# Marca todos os testes neste arquivo para usar pytest-asyncio
pytestmark = pytest.mark.asyncio


async def test_root_endpoint(client: AsyncClient):
    """Testa GET / (Root endpoint)"""
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert "message" in result
    assert "version" in result
    assert "docs" in result


async def test_health_check(client: AsyncClient):
    """Testa GET /health (Health check endpoint)"""
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["status"] == "healthy"
    assert "version" in result
