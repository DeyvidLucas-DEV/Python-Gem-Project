# Guia de Configuração CORS

## Problema Identificado
O backend na VPS estava bloqueando requisições do frontend rodando em `localhost` devido à configuração restritiva de CORS.

## Solução Implementada

### 1. Código Atualizado
- **`app/core/config.py`**: Agora suporta múltiplos formatos de configuração CORS
  - String com `*` para permitir todas as origens (desenvolvimento)
  - Lista JSON: `["origin1", "origin2"]`
  - String separada por vírgula: `origin1,origin2`

### 2. Configurações por Ambiente

#### Desenvolvimento Local (já configurado em `.env`)
```bash
BACKEND_CORS_ORIGINS=*
```
Isso permite que qualquer origem acesse o backend.

#### Produção na VPS
Edite o arquivo `.env` na sua VPS e configure assim:

**Opção 1 - Lista JSON:**
```bash
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","https://seu-dominio.com"]
```

**Opção 2 - Separado por vírgula (mais simples):**
```bash
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://seu-dominio.com
```

## Como Aplicar na VPS

### Passo 1: Atualizar o código na VPS
```bash
# SSH na VPS
ssh seu-usuario@sua-vps

# Navegue até o diretório do projeto
cd /caminho/do/projeto

# Puxe as atualizações
git pull origin main
```

### Passo 2: Atualizar o arquivo .env na VPS
```bash
# Edite o .env
nano .env

# Atualize a linha BACKEND_CORS_ORIGINS:
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Passo 3: Reiniciar o serviço
```bash
# Se estiver usando systemd
sudo systemctl restart seu-servico-fastapi

# Se estiver usando supervisor
sudo supervisorctl restart seu-servico-fastapi

# Ou se estiver rodando diretamente
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Importante - Segurança

### ⚠️ NÃO use `BACKEND_CORS_ORIGINS=*` em PRODUÇÃO!
Isso permite que qualquer site faça requisições ao seu backend, o que é um risco de segurança.

### ✅ Em produção, sempre especifique as origens permitidas:
```bash
# Se o frontend está em https://meusite.com:
BACKEND_CORS_ORIGINS=https://meusite.com

# Para múltiplas origens:
BACKEND_CORS_ORIGINS=https://meusite.com,https://app.meusite.com
```

## Testando

Após reiniciar o backend na VPS, teste fazendo uma requisição do seu frontend local:

```bash
# Teste com curl
curl -X OPTIONS http://ip-da-vps:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

Você deve ver nos headers de resposta:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

## Troubleshooting

### Problema: Ainda recebo erro CORS
1. Verifique se reiniciou o backend na VPS
2. Confirme que o arquivo `.env` foi atualizado corretamente
3. Verifique os logs do backend para confirmar que está lendo a configuração correta

### Problema: Funciona local mas não na VPS
1. Certifique-se de fazer `git pull` na VPS
2. Verifique se o `.env` na VPS tem a configuração correta
3. Reinicie o serviço do backend

### Ver logs do backend
```bash
# Se usando systemd
sudo journalctl -u seu-servico-fastapi -f

# Se usando supervisor
sudo tail -f /var/log/supervisor/seu-servico-fastapi.log
```
