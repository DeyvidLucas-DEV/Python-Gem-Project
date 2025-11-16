# Guia de Configuração do Jenkins

Este guia explica como configurar o Jenkins para executar testes automaticamente antes de cada deploy.

## 📋 O que o Pipeline Faz

O pipeline foi configurado com 6 etapas que **sempre** executam os testes:

### 1. **Checkout**
   - Baixa o código do repositório GitHub

### 2. **Setup**
   - Cria um ambiente virtual Python
   - Instala todas as dependências do `requirements.txt`

### 3. **Test** ⚠️ **ETAPA CRÍTICA**
   - Executa **TODOS** os testes com pytest
   - Gera relatórios de cobertura
   - **Se qualquer teste falhar, o pipeline PARA aqui**
   - Deploy **NÃO** acontece se testes falharem

### 4. **Code Quality** (Opcional)
   - Verifica qualidade do código
   - Pode adicionar flake8, black, etc.

### 5. **Build**
   - Constrói a imagem Docker
   - Só executa se os testes passarem

### 6. **Deploy**
   - Faz deploy da aplicação
   - **Só executa se TODAS as etapas anteriores passarem**

## 🔒 Garantias de Qualidade

### ✅ O que o pipeline garante:

1. **Testes sempre executam** antes do deploy
2. **Deploy só acontece** se 100% dos testes passarem
3. **Relatórios de teste** são gerados e arquivados
4. **Cobertura de código** é medida
5. **Notificações** de sucesso/falha

### ❌ O que NÃO pode acontecer:

- Deploy sem executar testes
- Deploy com testes falhando
- Código quebrado em produção

## 🚀 Como Usar

### Configuração Inicial no Jenkins

1. **Instalar Plugins Necessários:**
   - Git Plugin
   - Pipeline Plugin
   - JUnit Plugin (para relatórios de teste)
   - HTML Publisher Plugin (opcional, para relatórios de cobertura)

2. **Criar Credenciais:**
   - No Jenkins, vá em: `Manage Jenkins` → `Credentials`
   - Adicione uma credencial com ID: `github-pat`
   - Tipo: Username with password ou Secret text
   - Use seu GitHub Personal Access Token

3. **Criar o Job:**
   - New Item → Pipeline
   - Em "Pipeline", selecione "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/DeyvidLucas-DEV/Python-Gem-Project`
   - Credentials: Selecione `github-pat`
   - Branch: `main`
   - Script Path: `Jenkinsfile`

4. **Configurar Triggers (já está no Jenkinsfile):**
   ```groovy
   triggers {
       pollSCM('* * * * *') // Verifica por mudanças a cada minuto
   }
   ```

## 📊 Visualizando Resultados dos Testes

### No Console do Jenkins:

```
[Test] Executing testes automatizados...
============================= test session starts ==============================
collected 15 items

tests/test_publicacao.py::test_create_publicacao PASSED              [  6%]
tests/test_publicacao.py::test_create_publicacao_tipo_materia PASSED [ 13%]
tests/test_publicacao.py::test_create_publicacao_all_enum_types[materia] PASSED [ 20%]
...

---------- coverage: platform linux, python 3.11.5 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
app/api/v1/endpoints/publicacoes.py  120     10    92%   45-48, 67
app/crud/publicacao.py                85      5    94%   102-106
app/models/publicacao.py              30      0   100%
---------------------------------------------------------------
TOTAL                               1234     89    93%

========================= 15 passed in 5.43s ===============================
```

### Artefatos Gerados:

- `test-results.xml` - Resultados dos testes (JUnit format)
- `htmlcov/index.html` - Relatório visual de cobertura
- `coverage.xml` - Cobertura em formato XML

## ⚙️ Customizações Disponíveis

### 1. Adicionar Verificação de Estilo (Flake8)

Descomente no stage "Code Quality":

```groovy
stage('Code Quality') {
    steps {
        sh '''
            . ${VENV_PATH}/bin/activate
            pip install flake8
            flake8 app/ --max-line-length=120 --exclude=.venv,__pycache__
        '''
    }
}
```

Adicione ao `requirements.txt`:
```
flake8==7.0.0
```

### 2. Adicionar Health Check após Deploy

Descomente no stage "Deploy":

```groovy
# Health check
curl -f http://localhost:8000/health || exit 1
```

### 3. Habilitar Relatório de Cobertura HTML

Descomente no stage "Test" → post → always:

```groovy
publishHTML([
    allowMissing: false,
    alwaysLinkToLastBuild: true,
    keepAll: true,
    reportDir: 'htmlcov',
    reportFiles: 'index.html',
    reportName: 'Coverage Report'
])
```

### 4. Adicionar Notificações

No bloco `post`:

```groovy
post {
    success {
        // Slack
        slackSend(
            color: 'good',
            message: "✅ Deploy realizado com sucesso! Todos os testes passaram."
        )

        // Email
        emailext(
            subject: "✅ Build #${BUILD_NUMBER} - Success",
            body: "Pipeline concluído. Testes: PASSOU",
            to: "team@example.com"
        )
    }
    failure {
        slackSend(
            color: 'danger',
            message: "❌ Build falhou! Testes não passaram."
        )
    }
}
```

## 🔍 Como Verificar se os Testes Estão Rodando

### 1. Via Jenkins UI:
- Abra o job no Jenkins
- Clique em "Console Output"
- Procure pela seção `[Test]`
- Veja todos os testes executados

### 2. Via Resultados de Teste:
- No job, clique em "Test Result"
- Veja o gráfico de testes ao longo do tempo
- Veja quais testes passaram/falharam

### 3. Via Artefatos:
- No job, clique em "Last Successful Artifacts"
- Baixe `test-results.xml` ou `htmlcov`

## 🛡️ Cenários de Falha

### Cenário 1: Teste Falha

```
Stage: Test
Status: FAILED ❌
Resultado: Pipeline PARA aqui, deploy NÃO acontece

Console Output:
FAILED tests/test_publicacao.py::test_create_publicacao - AssertionError
❌ Pipeline falhou!
ERRO: Testes falharam! Deploy cancelado.
```

### Cenário 2: Todos os Testes Passam

```
Stage: Test → PASSED ✅
Stage: Code Quality → PASSED ✅
Stage: Build → PASSED ✅
Stage: Deploy → PASSED ✅

Console Output:
✅ Pipeline concluído com sucesso!
Testes: PASSOU ✓
Deploy: COMPLETO ✓
```

## 📈 Métricas e Monitoramento

O Jenkins automaticamente rastreia:

- **Taxa de sucesso/falha** do build
- **Duração dos testes** ao longo do tempo
- **Cobertura de código** (se habilitado)
- **Testes que falharam** com frequência
- **Histórico de builds**

## 🔧 Troubleshooting

### Problema: Testes não executam

**Solução:**
```bash
# Verificar se pytest está instalado
. .venv/bin/activate
which pytest

# Verificar se conftest.py existe
ls tests/conftest.py

# Executar manualmente
pytest tests/ -v
```

### Problema: Deploy acontece mesmo com testes falhando

**Verificar:**
- O stage "Deploy" tem a condição `when`?
- Os testes realmente falharam ou só warnings?
- Verificar console output completo

### Problema: Cobertura não é gerada

**Solução:**
```bash
# Instalar pytest-cov
pip install pytest-cov

# Adicionar ao requirements.txt
echo "pytest-cov==6.0.0" >> requirements.txt
```

## 📝 Checklist de Configuração

- [ ] Jenkinsfile está no repositório
- [ ] Credencial `github-pat` configurada
- [ ] Job criado no Jenkins
- [ ] Primeiro build executado com sucesso
- [ ] Testes aparecem no console output
- [ ] Relatórios de teste são gerados
- [ ] Deploy só acontece se testes passarem
- [ ] Notificações configuradas (opcional)

## 🎯 Resultado Final

Com esta configuração, você tem **garantia absoluta** que:

1. ✅ Todo código que vai para produção passou pelos testes
2. ✅ Jenkins executa testes automaticamente a cada commit
3. ✅ Deploy só acontece se tudo estiver OK
4. ✅ Você tem visibilidade total do status dos testes
5. ✅ Relatórios de cobertura são gerados automaticamente

---

**Dúvidas?** Verifique os logs do Jenkins em "Console Output" de cada build.
