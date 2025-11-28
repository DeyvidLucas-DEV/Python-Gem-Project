#!/bin/bash
# Script de configuração inicial do servidor
# Execute uma vez no servidor: bash setup-server.sh

set -e

echo "=== Configurando servidor para GEM Project ==="

# 1. Criar diretórios
echo "Criando diretórios..."
sudo mkdir -p /var/www/gem-project
sudo mkdir -p /var/data/gem-project/uploads
sudo chown -R $USER:$USER /var/www/gem-project
sudo chown -R $USER:$USER /var/data/gem-project

# 2. Clonar repositório (se não existir)
if [ ! -d "/var/www/gem-project/.git" ]; then
    echo "Clonando repositório..."
    git clone https://github.com/DeyvidLucas-DEV/Python-Gem-Project.git /var/www/gem-project
else
    echo "Repositório já existe, atualizando..."
    cd /var/www/gem-project
    git pull origin main
fi

cd /var/www/gem-project

# 3. Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "Criando arquivo .env..."
    cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://root:!$GEM2026e@161.97.180.189:5432/gem_db

# Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production

# Storage
UPLOADS_PATH=/var/data/uploads
EOF
    echo "IMPORTANTE: Edite o arquivo .env com suas credenciais!"
fi

# 4. Instalar Docker se não existir
if ! command -v docker &> /dev/null; then
    echo "Instalando Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Docker instalado. Faça logout e login novamente."
fi

# 5. Build e start dos containers
echo "Iniciando containers..."
docker compose down 2>/dev/null || true
docker compose build
docker compose up -d

# 6. Mostrar status
echo ""
echo "=== Setup completo! ==="
echo "Containers rodando:"
docker ps
echo ""
echo "Acesse: http://$(curl -s ifconfig.me)"
echo "API Docs: http://$(curl -s ifconfig.me)/api/v1/docs"
echo "Logs: docker compose logs -f"
