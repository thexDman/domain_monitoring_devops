pipeline {
    agent { label 'docker' }

    options {
        ansiColor('xterm')
        timestamps()
    }

    environment {
        REGISTRY = "thexDman"

        BE_IMAGE = "domain-monitoring-be"
        FE_IMAGE = "domain-monitoring-fe"

        COMPOSE_FILE = "docker-compose.ci.yml"

        DOCKERHUB = credentials('dockerhub-creds')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git rev-parse --short HEAD'
            }
        }

        stage('Build Backend Image') {
            steps {
                sh """
                  docker build \
                    -t ${BE_IMAGE}:ci \
                    backend
                """
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh """
                  docker build \
                    -t ${FE_IMAGE}:ci \
                    frontend
                """
            }
        }

        stage('Start Environment (docker-compose)') {
            steps {
                sh """
                  docker-compose -f ${COMPOSE_FILE} down -v || true
                  docker-compose -f ${COMPOSE_FILE} up -d
                """
            }
        }

        stage('Wait for Backend Health') {
            steps {
                sh """
                  echo "Waiting for backend health..."
                  for i in {1..30}; do
                    curl -sf http://localhost:8080/api/health && exit 0
                    sleep 2
                  done
                  echo "Backend did not become healthy"
                  exit 1
                """
            }
        }

        stage('Run API Tests') {
            steps {
                sh """
                  pytest tests/api_tests
                """
            }
        }

        stage('Run Selenium UI Tests') {
            steps {
                sh """
                  pytest tests/selenium_tests
                """
            }
        }

        stage('Push Images (latest only)') {
            steps {
                sh """
                  echo ${DOCKERHUB_PSW} | docker login -u ${DOCKERHUB_USR} --password-stdin

                  docker tag ${BE_IMAGE}:ci ${DOCKERHUB_USR}/${BE_IMAGE}:latest
                  docker tag ${FE_IMAGE}:ci ${DOCKERHUB_USR}/${FE_IMAGE}:latest

                  docker push ${DOCKERHUB_USR}/${BE_IMAGE}:latest
                  docker push ${DOCKERHUB_USR}/${FE_IMAGE}:latest

                  docker logout
                """
            }
        }
    }

    post {
        always {
            sh """
              docker-compose -f ${COMPOSE_FILE} down -v || true
            """
        }

        failure {
            sh """
              docker ps -a
              docker logs dms-backend || true
              docker logs dms-frontend || true
            """
        }
    }
}
