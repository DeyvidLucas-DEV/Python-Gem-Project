from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from datetime import datetime
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.utils.exceptions import (
    validation_exception_handler,
    integrity_error_handler,
    general_exception_handler
)
from app.utils.metrics import get_all_metrics

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)



def create_application() -> FastAPI:
    """Factory para criar a aplicação FastAPI."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Handlers de exceção
    app.add_exception_handler(ValueError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    @app.get("/")
    async def root():
        """Endpoint de health check."""
        return {
            "message": f"Bem-vindo ao {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs"
        }

    @app.get("/health")
    async def health_check(detailed: bool = False):
        """
        Endpoint de verificação de saúde da aplicação.
        Verifica a API e a conexão com o banco de dados.

        Args:
            detailed: Se True, retorna métricas detalhadas de infraestrutura
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "service": settings.PROJECT_NAME,
            "checks": {
                "api": "healthy",
                "database": "unknown"
            }
        }

        # Verificar conexão com o banco de dados
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Health check failed - Database error: {e}")

        # Adicionar métricas detalhadas se solicitado
        if detailed:
            try:
                health_status["metrics"] = get_all_metrics()
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                health_status["metrics_error"] = str(e)

        return health_status

    @app.get("/health/ui", response_class=HTMLResponse)
    async def health_ui():
        """
        Interface HTML para visualização de métricas de saúde e infraestrutura.
        """
        html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Monitoramento - Health Check</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }

        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            margin: 10px 0;
        }

        .status-healthy {
            background: #10b981;
            color: white;
        }

        .status-unhealthy {
            background: #ef4444;
            color: white;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .card h2 {
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .metric-row:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #6b7280;
            font-weight: 500;
        }

        .metric-value {
            color: #1f2937;
            font-weight: 600;
        }

        .progress-bar {
            width: 100%;
            height: 25px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
            transition: width 0.5s ease;
        }

        .progress-fill.warning {
            background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);
        }

        .progress-fill.danger {
            background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
        }

        .disk-item {
            margin-bottom: 20px;
            padding: 15px;
            background: #f9fafb;
            border-radius: 10px;
        }

        .disk-item h3 {
            color: #4b5563;
            font-size: 1.1em;
            margin-bottom: 10px;
        }

        .auto-refresh {
            text-align: center;
            margin-top: 20px;
            color: white;
            font-size: 0.9em;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #6b7280;
        }

        .icon {
            font-size: 1.3em;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .spinner {
            display: inline-block;
            animation: spin 1s linear infinite;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Sistema de Monitoramento</h1>
            <div id="service-name"></div>
            <div id="status-badge"></div>
            <div id="timestamp"></div>
        </div>

        <div id="content" class="loading">
            <div class="spinner">⏳</div> Carregando métricas...
        </div>

        <div class="auto-refresh">
            🔄 Atualização automática a cada 5 segundos
        </div>
    </div>

    <script>
        async function fetchHealthData() {
            try {
                const response = await fetch('/health?detailed=true');
                const data = await response.json();
                renderHealth(data);
            } catch (error) {
                document.getElementById('content').innerHTML =
                    '<div class="card"><h2>❌ Erro ao carregar dados</h2><p>' + error.message + '</p></div>';
            }
        }

        function renderHealth(data) {
            // Header
            document.getElementById('service-name').innerHTML =
                `<p style="color: #6b7280; font-size: 1.1em;">${data.service} v${data.version}</p>`;

            const statusClass = data.status === 'healthy' ? 'status-healthy' : 'status-unhealthy';
            document.getElementById('status-badge').innerHTML =
                `<span class="status-badge ${statusClass}">${data.status.toUpperCase()}</span>`;

            document.getElementById('timestamp').innerHTML =
                `<p style="color: #6b7280; margin-top: 10px;">Última atualização: ${new Date(data.timestamp).toLocaleString('pt-BR')}</p>`;

            if (!data.metrics) {
                document.getElementById('content').innerHTML =
                    '<div class="card"><h2>ℹ️ Métricas não disponíveis</h2></div>';
                return;
            }

            const metrics = data.metrics;

            // Render content
            let html = '<div class="grid">';

            // System Info
            html += `
                <div class="card">
                    <h2><span class="icon">💻</span> Informações do Sistema</h2>
                    <div class="metric-row">
                        <span class="metric-label">Tempo de atividade</span>
                        <span class="metric-value">${metrics.system.uptime_days.toFixed(2)} dias</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Horas ativas</span>
                        <span class="metric-value">${metrics.system.uptime_hours.toFixed(2)} h</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Boot time</span>
                        <span class="metric-value">${new Date(metrics.system.boot_time).toLocaleString('pt-BR')}</span>
                    </div>
                </div>
            `;

            // CPU
            const cpuClass = metrics.cpu.usage_percent > 80 ? 'danger' : metrics.cpu.usage_percent > 60 ? 'warning' : '';
            html += `
                <div class="card">
                    <h2><span class="icon">⚡</span> CPU</h2>
                    <div class="metric-row">
                        <span class="metric-label">Uso</span>
                        <span class="metric-value">${metrics.cpu.usage_percent}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${cpuClass}" style="width: ${metrics.cpu.usage_percent}%">
                            ${metrics.cpu.usage_percent}%
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Núcleos lógicos</span>
                        <span class="metric-value">${metrics.cpu.cores_logical}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Núcleos físicos</span>
                        <span class="metric-value">${metrics.cpu.cores_physical}</span>
                    </div>
                    ${metrics.cpu.frequency ? `
                        <div class="metric-row">
                            <span class="metric-label">Frequência atual</span>
                            <span class="metric-value">${metrics.cpu.frequency.current} MHz</span>
                        </div>
                    ` : ''}
                </div>
            `;

            // Memory
            const memClass = metrics.memory.percent > 80 ? 'danger' : metrics.memory.percent > 60 ? 'warning' : '';
            html += `
                <div class="card">
                    <h2><span class="icon">🧠</span> Memória RAM</h2>
                    <div class="metric-row">
                        <span class="metric-label">Uso</span>
                        <span class="metric-value">${metrics.memory.percent}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${memClass}" style="width: ${metrics.memory.percent}%">
                            ${metrics.memory.percent}%
                        </div>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Total</span>
                        <span class="metric-value">${metrics.memory.total_gb} GB</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Usado</span>
                        <span class="metric-value">${metrics.memory.used_gb} GB</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Disponível</span>
                        <span class="metric-value">${metrics.memory.available_gb} GB</span>
                    </div>
                    ${metrics.memory.swap.total > 0 ? `
                        <div class="metric-row">
                            <span class="metric-label">Swap usado</span>
                            <span class="metric-value">${metrics.memory.swap.percent}%</span>
                        </div>
                    ` : ''}
                </div>
            `;

            // Process
            html += `
                <div class="card">
                    <h2><span class="icon">🔧</span> Processo da Aplicação</h2>
                    <div class="metric-row">
                        <span class="metric-label">PID</span>
                        <span class="metric-value">${metrics.process.pid}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">CPU</span>
                        <span class="metric-value">${metrics.process.cpu_percent}%</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Memória RSS</span>
                        <span class="metric-value">${metrics.process.memory_rss_mb} MB</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Memória VMS</span>
                        <span class="metric-value">${metrics.process.memory_vms_mb} MB</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Threads</span>
                        <span class="metric-value">${metrics.process.threads}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Criado em</span>
                        <span class="metric-value">${new Date(metrics.process.create_time).toLocaleString('pt-BR')}</span>
                    </div>
                </div>
            `;

            // Network
            html += `
                <div class="card">
                    <h2><span class="icon">🌐</span> Rede</h2>
                    <div class="metric-row">
                        <span class="metric-label">Dados enviados</span>
                        <span class="metric-value">${metrics.network.bytes_sent_mb} MB</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Dados recebidos</span>
                        <span class="metric-value">${metrics.network.bytes_recv_mb} MB</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Pacotes enviados</span>
                        <span class="metric-value">${metrics.network.packets_sent.toLocaleString()}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Pacotes recebidos</span>
                        <span class="metric-value">${metrics.network.packets_recv.toLocaleString()}</span>
                    </div>
                    ${metrics.network.errin + metrics.network.errout > 0 ? `
                        <div class="metric-row">
                            <span class="metric-label">Erros (in/out)</span>
                            <span class="metric-value" style="color: #ef4444;">${metrics.network.errin} / ${metrics.network.errout}</span>
                        </div>
                    ` : ''}
                </div>
            `;

            html += '</div>';

            // Disk (full width)
            if (metrics.disk.partitions && metrics.disk.partitions.length > 0) {
                html += `
                    <div class="card">
                        <h2><span class="icon">💾</span> Armazenamento</h2>
                `;

                metrics.disk.partitions.forEach(disk => {
                    const diskClass = disk.percent > 80 ? 'danger' : disk.percent > 60 ? 'warning' : '';
                    html += `
                        <div class="disk-item">
                            <h3>${disk.device} - ${disk.mountpoint}</h3>
                            <div class="metric-row">
                                <span class="metric-label">Tipo</span>
                                <span class="metric-value">${disk.fstype}</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Uso</span>
                                <span class="metric-value">${disk.percent}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill ${diskClass}" style="width: ${disk.percent}%">
                                    ${disk.percent}%
                                </div>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Total</span>
                                <span class="metric-value">${disk.total_gb} GB</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Usado</span>
                                <span class="metric-value">${disk.used_gb} GB</span>
                            </div>
                            <div class="metric-row">
                                <span class="metric-label">Livre</span>
                                <span class="metric-value">${disk.free_gb} GB</span>
                            </div>
                        </div>
                    `;
                });

                if (metrics.disk.io_counters) {
                    html += `
                        <h3 style="margin-top: 20px; color: #4b5563;">Estatísticas de I/O</h3>
                        <div class="metric-row">
                            <span class="metric-label">Leituras</span>
                            <span class="metric-value">${metrics.disk.io_counters.read_mb} MB</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Escritas</span>
                            <span class="metric-value">${metrics.disk.io_counters.write_mb} MB</span>
                        </div>
                    `;
                }

                html += '</div>';
            }

            document.getElementById('content').innerHTML = html;
        }

        // Initial load
        fetchHealthData();

        // Auto refresh every 5 seconds
        setInterval(fetchHealthData, 5000);
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
