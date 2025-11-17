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
    # Status pode ser healthy ou unhealthy dependendo do banco de dados
    assert result["status"] in ["healthy", "unhealthy"]
    assert "version" in result
    assert "timestamp" in result
    assert "service" in result
    assert "checks" in result

    # Verificar se os checks de componentes estão presentes
    checks = result["checks"]
    assert "api" in checks
    assert "database" in checks
    assert checks["api"] == "healthy"
    # Database pode estar healthy ou unhealthy no ambiente de testes
    assert checks["database"] in ["healthy", "unhealthy"]


async def test_health_check_detailed(client: AsyncClient):
    """Testa GET /health?detailed=true (Health check com métricas detalhadas)"""
    response = await client.get("/health?detailed=true")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    # Status pode ser healthy ou unhealthy dependendo do banco de dados
    assert result["status"] in ["healthy", "unhealthy"]
    assert "version" in result
    assert "timestamp" in result
    assert "service" in result
    assert "checks" in result
    assert "metrics" in result

    # Verificar se todas as métricas estão presentes
    metrics = result["metrics"]
    assert "timestamp" in metrics
    assert "system" in metrics
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert "network" in metrics
    assert "process" in metrics

    # Verificar métricas de CPU
    cpu = metrics["cpu"]
    assert "usage_percent" in cpu
    assert "cores_logical" in cpu
    assert "cores_physical" in cpu
    assert isinstance(cpu["usage_percent"], (int, float))
    assert cpu["usage_percent"] >= 0
    assert cpu["usage_percent"] <= 100

    # Verificar métricas de memória
    memory = metrics["memory"]
    assert "total_gb" in memory
    assert "used_gb" in memory
    assert "available_gb" in memory
    assert "percent" in memory
    assert memory["percent"] >= 0
    assert memory["percent"] <= 100

    # Verificar métricas de disco
    disk = metrics["disk"]
    assert "partitions" in disk
    assert isinstance(disk["partitions"], list)

    # Verificar métricas de rede
    network = metrics["network"]
    assert "bytes_sent" in network
    assert "bytes_recv" in network

    # Verificar métricas de processo
    process = metrics["process"]
    assert "pid" in process
    assert "cpu_percent" in process
    assert "memory_rss_mb" in process
    assert isinstance(process["pid"], int)


async def test_health_ui(client: AsyncClient):
    """Testa GET /health/ui (Interface HTML de health check)"""
    response = await client.get("/health/ui")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/html")

    # Verificar se é um HTML válido
    content = response.text
    assert "<!DOCTYPE html>" in content
    assert "<html" in content
    assert "Dashboard de Monitoramento" in content
    assert "fetchHealthData" in content  # Verificar se tem a função JavaScript
    assert "Chart.js" in content  # Verificar se tem Chart.js
    assert "chart-card" in content  # Verificar se tem os cards de gráfico
