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
                    -f backend/Dockerfile \
                    .
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

        stage('Backend Sanity Checks') {
            steps {
                sh '''
                echo "==== Docker PS ===="
                docker ps -a

                echo "==== Backend logs ===="
                docker-compose -f docker-compose.ci.yml logs backend || true

                echo "==== Inspect backend container ===="
                docker inspect domain-monitoring-ci-backend-1 || true

                echo "==== Try running backend manually ===="
                docker-compose -f docker-compose.ci.yml run --rm backend python -c "import backend.app; print('IMPORT OK')" || true
                '''
            }
        }

        stage('Wait for Backend Health') {
            steps {
                sh '''
                    echo "Waiting for backend health..."
                    for i in {1..10}; do
                    if docker-compose -f docker-compose.ci.yml exec backend \
                        curl -sf http://localhost:8080/api/health; then
                        echo "Backend is healthy"
                        exit 0
                    fi
                    sleep 2
                    done
                    echo "Backend did not become healthy"
                    exit 1
                '''
            }
        }

        stage('Run API Tests') {
            steps {
                sh """
                docker-compose -f docker-compose.ci.yml exec \
                    -e BASE_URL=http://localhost:8080 \
                    backend \
                    pytest tests/api_tests --maxfail=1 --disable-warnings -q
                """
            }
        }

        stage('Run Selenium UI Tests') {
            steps {
                sh """
                docker-compose -f docker-compose.ci.yml exec \
                    -e BASE_URL=http://frontend \
                    backend \
                    pytest tests/selenium_tests --maxfail=1 --disable-warnings -q
                """
            }
        }

        stage('Compute Semantic Version') {
            steps {
                script {
                    echo "Fetching existing tags from Docker Hub..."

                    def image = "${DOCKERHUB_USR}/${BE_IMAGE}"

                    def tagsJson = sh(
                        script: "curl -s https://hub.docker.com/v2/repositories/${image}/tags?page_size=100",
                        returnStdout: true
                    )

                    def parsed = new groovy.json.JsonSlurper().parseText(tagsJson)

                    def semverTags = parsed.results
                        .collect { it.name }
                        .findAll { it ==~ /v\\d+\\.\\d+\\.\\d+/ }

                    echo "Found semantic tags: ${semverTags}"

                    String nextVersion

                    if (!semverTags || semverTags.isEmpty()) {
                        nextVersion = "v1.0.0"
                    } else {
                        semverTags.sort { a, b ->
                            def av = a.replace("v","").split("\\.").collect { it.toInteger() }
                            def bv = b.replace("v","").split("\\.").collect { it.toInteger() }
                            av <=> bv
                        }

                        def latest = semverTags.last()
                        def parts = latest.replace("v","").split("\\.").collect { it.toInteger() }
                        parts[2] = parts[2] + 1

                        nextVersion = "v${parts[0]}.${parts[1]}.${parts[2]}"
                    }

                    env.SEMVER_TAG = nextVersion
                    echo "Next semantic version: ${env.SEMVER_TAG}"
                }
            }
        }


        stage('Push Images (latest + semantic)') {
            steps {
                sh """
                echo ${DOCKERHUB_PSW} | docker login -u ${DOCKERHUB_USR} --password-stdin

                # Backend
                docker tag ${BE_IMAGE}:ci ${DOCKERHUB_USR}/${BE_IMAGE}:latest
                docker tag ${BE_IMAGE}:ci ${DOCKERHUB_USR}/${BE_IMAGE}:${SEMVER_TAG}

                docker push ${DOCKERHUB_USR}/${BE_IMAGE}:latest
                docker push ${DOCKERHUB_USR}/${BE_IMAGE}:${SEMVER_TAG}

                # Frontend
                docker tag ${FE_IMAGE}:ci ${DOCKERHUB_USR}/${FE_IMAGE}:latest
                docker tag ${FE_IMAGE}:ci ${DOCKERHUB_USR}/${FE_IMAGE}:${SEMVER_TAG}

                docker push ${DOCKERHUB_USR}/${FE_IMAGE}:latest
                docker push ${DOCKERHUB_USR}/${FE_IMAGE}:${SEMVER_TAG}

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
