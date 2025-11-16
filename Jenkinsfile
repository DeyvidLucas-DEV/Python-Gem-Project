// Jenkinsfile
pipeline {
    agent any

    triggers {
        pollSCM('* * * * *') // Verifica por mudanças a cada minuto
    }

    environment {
        // Variáveis de ambiente para testes
        PYTHON_VERSION = 'python3'
        VENV_PATH = "${WORKSPACE}/.venv"
    }

    stages {
        // Fase 1: Baixar o código do GitHub
        stage('Checkout') {
            steps {
                cleanWs() // Limpa o workspace antes de baixar
                echo 'Baixando código do repositório...'
                git credentialsId: 'github-pat',
                    url: 'https://github.com/DeyvidLucas-DEV/Python-Gem-Project',
                    branch: 'main'
            }
        }

        // Fase 2: Configurar ambiente de testes
        stage('Setup') {
            steps {
                echo 'Configurando ambiente virtual Python...'
                sh '''
                    # Criar ambiente virtual
                    ${PYTHON_VERSION} -m venv ${VENV_PATH}

                    # Ativar e instalar dependências
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // Fase 3: Executar testes
        stage('Test') {
            steps {
                echo 'Executando testes automatizados...'
                sh '''
                    . ${VENV_PATH}/bin/activate

                    # Executar pytest com cobertura
                    pytest tests/ -v \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml \
                        --cov-report=html \
                        --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    // Publica os resultados dos testes
                    junit 'test-results.xml'

                    // Publica relatório de cobertura (se tiver o plugin)
                    // publishHTML([
                    //     allowMissing: false,
                    //     alwaysLinkToLastBuild: true,
                    //     keepAll: true,
                    //     reportDir: 'htmlcov',
                    //     reportFiles: 'index.html',
                    //     reportName: 'Coverage Report'
                    // ])
                }
                failure {
                    echo 'ERRO: Testes falharam! Deploy cancelado.'
                }
            }
        }

        // Fase 4: Lint e Qualidade de Código (Opcional)
        stage('Code Quality') {
            steps {
                echo 'Verificando qualidade do código...'
                sh '''
                    . ${VENV_PATH}/bin/activate

                    # Verificar estilo de código com flake8 (se instalado)
                    # pip install flake8
                    # flake8 app/ --max-line-length=120 --exclude=.venv,__pycache__

                    echo "Code quality check completo (adicione flake8/black se desejar)"
                '''
            }
        }

        // Fase 5: Build da imagem Docker
        stage('Build') {
            steps {
                echo 'Construindo imagem Docker...'
                sh '''
                    # Build da imagem
                    /usr/bin/python3 /usr/bin/docker-compose -f docker-compose.yml build
                '''
            }
        }

        // Fase 6: Deploy (só executa se os testes passarem)
        stage('Deploy') {
            when {
                // Só faz deploy se todas as etapas anteriores passarem
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Iniciando deploy...'
                sh '''
                    # Parar containers antigos
                    /usr/bin/python3 /usr/bin/docker-compose -f docker-compose.yml down

                    # Subir novos containers
                    /usr/bin/python3 /usr/bin/docker-compose -f docker-compose.yml up -d

                    # Limpar imagens antigas
                    docker image prune -f

                    # Aguardar a aplicação iniciar
                    sleep 10

                    # Health check (opcional)
                    # curl -f http://localhost:8000/health || exit 1
                '''
                echo 'Deploy finalizado com sucesso!'
            }
            post {
                success {
                    echo 'Aplicação deployada e rodando!'
                }
                failure {
                    echo 'ERRO: Deploy falhou! Tentando rollback...'
                    // Adicionar lógica de rollback se necessário
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline concluído com sucesso!'
            echo 'Testes: PASSOU ✓'
            echo 'Deploy: COMPLETO ✓'
            // Adicionar notificação (Slack, Email, etc.)
        }
        failure {
            echo '❌ Pipeline falhou!'
            echo 'Verifique os logs para detalhes do erro.'
            // Adicionar notificação de erro
        }
        always {
            // Limpar ambiente virtual para economizar espaço
            sh 'rm -rf ${VENV_PATH} || true'

            // Arquivar artefatos importantes
            archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
            archiveArtifacts artifacts: 'htmlcov/**/*', allowEmptyArchive: true
        }
    }
}

