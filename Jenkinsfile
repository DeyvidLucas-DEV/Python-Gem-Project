// Jenkinsfile
pipeline {
    agent any // Roda em qualquer agente disponível

    stages {
        // Fase 1: Baixar o código do GitHub
        stage('Checkout') {
            steps {
                cleanWs() // Limpa o workspace antes de baixar
                // Usa a credencial 'github-pat' para acessar o repositório
                git credentialsId: 'github-pat', url: 'https://github.com/DeyvidLucas-DEV/Python-Gem-Project', branch: 'main'
            }
        }

        // Fase 2: Rodar testes (Placeholder - adicione seus comandos de teste aqui)
        stage('Test') {
            steps {
                sh 'echo "Executando testes (ex: pytest)..."'
                // Exemplo: sh 'pytest'
                // Se os testes precisarem rodar dentro do ambiente Docker:
                // sh 'docker-compose -f docker-compose.yml run --rm app pytest'
            }
        }

        // Fase 3: Buildar a imagem Docker e fazer Deploy com Docker Compose
        sstage('Build & Deploy') {
            steps {
                sh 'echo "Iniciando build e deploy..."'
                // Usando caminho completo
                sh '/usr/bin/docker-compose -f docker-compose.yml down'
                sh '/usr/bin/docker-compose -f docker-compose.yml up -d --build'
                sh 'docker image prune -f'
                sh 'echo "Deploy finalizado!"'
            }
        }
    }
    }

    post {
        success {
            echo 'Pipeline concluído com sucesso!'
            // Ex: Enviar notificação
        }
        failure {
            echo 'Pipeline falhou!'
            // Ex: Enviar notificação de erro
        }
    }
}