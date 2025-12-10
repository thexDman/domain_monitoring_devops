pipeline {
    agent { label 'Slave docker' }

    options {
        ansiColor('xterm')
        timestamps()
    }
    
    environment {
        REGISTRY = "thexDman"
        IMAGE_NAME = "domain_monitoring_devops"
        APP_PORT = "8080"
        CONTAINER_NAME = "DMS-TEMP-${BUILD_NUMBER}"
        DOCKERHUB = credentials('dockerhub-creds')
        GITHUB = credentials('github-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh '''
                    echo "---Git INFO---"
                    echo "Branch: $GIT_BRANCH"
                    echo "Commit: $GIT_COMMIT"
                ''' 
            }
        }

        stage('Show node info') {
            steps {
                sh '''
                    echo "HOSTNAME: $(hostname)"
                    echo "USER: $(whoami)"
                    echo "WORKSPACE: $WORKSPACE"
                ''' 
            }
        }

        stage('Compute Image Tag') {
            steps {
                script {
                    env.SHORT_COMMIT = sh(
                        script: 'git rev-parse --short=8 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_TAG = "build-${BUILD_NUMBER}-${env.SHORT_COMMIT}"
                    echo "Docker image tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    echo "Building Docker image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Run Container for Tests') {
            steps {
                sh """
                    echo "Starting temporary container: ${CONTAINER_NAME}"

                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:8080 \
                        ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Waiting for app to start..."
                    sleep 10

                    echo "Health check (optional):"
                    curl -sS http://localhost:${APP_PORT} || echo "App not responding yet, tests may fail."
                """
            }
        }        

        stage('Execute Tests inside Container') {
            parallel {

                stage('API Tests') {
                    steps {
                        sh """
                            echo "Running API tests inside container..."
                            docker exec ${CONTAINER_NAME} pytest tests/api_tests --maxfail=1 --disable-warnings -q
                        """
                    }
                }

                stage('UI Selenium Tests') {
                    steps {
                        sh """
                            echo "Running Selenium/UI tests inside container..."
                            docker exec ${CONTAINER_NAME} pytest tests/selenium_tests --maxfail=1 --disable-warnings -q
                        """
                    }
                }

            }
        }

        stage('Push Docker Image') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                sh """
                    echo "Logging into Docker Hub as ${DOCKERHUB_USR}"
                    echo ${DOCKERHUB_PSW} | docker login -u ${DOCKERHUB_USR} --password-stdin

                    echo "Tagging image for Docker Hub..."
                    docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USR}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USR}/${IMAGE_NAME}:latest

                    echo "Pushing images..."
                    docker push ${DOCKERHUB_USR}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKERHUB_USR}/${IMAGE_NAME}:latest

                    docker logout
                """
            }
        }
    }
    post {
        failure {
            echo "Tests FAILED — dumping container logs..."
            sh """
                docker logs ${CONTAINER_NAME} || true
            """
        }

        always {
            echo "Cleaning temp containers & images..."
            sh """
                docker rm -f ${CONTAINER_NAME} || true
                # optional, if you don't want aggressive prune, comment this out:
                # docker system prune -af --volumes || true
            """
        }    
    }
}