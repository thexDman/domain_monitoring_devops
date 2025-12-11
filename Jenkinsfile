pipeline {
    agent { label 'docker' }

    options {
        ansiColor('xterm')
        timestamps()
    }

    environment {
        REGISTRY       = "thexDman"                  // local/CI registry namespace
        IMAGE_NAME     = "domain_monitoring_devops" // repo/image name
        APP_PORT       = "8080"
        CONTAINER_NAME = "DMS-TEMP-${BUILD_NUMBER}"

        // Jenkins credentials IDs created by JCasC:
        DOCKERHUB = credentials('dockerhub-creds')  // gives DOCKERHUB_USR / DOCKERHUB_PSW
        GITHUB    = credentials('github-token')     // gives GITHUB_USR / GITHUB_PSW
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh '''
                    echo "--- Git INFO ---"
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

        stage('Compute CI Image Tag') {
            steps {
                script {
                    env.SHORT_COMMIT = sh(
                        script: 'git rev-parse --short=8 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_TAG = "build-${BUILD_NUMBER}-${env.SHORT_COMMIT}"
                    echo "CI Docker image tag: ${env.IMAGE_TAG}"
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

        stage('Compute Next Semantic Version') {
            steps {
                script {
                    sh 'git fetch --tags'

                    def CURRENT_VERSION = sh(
                        script: "git tag --sort=-v:refname | grep -Eo 'v[0-9]+\\.[0-9]+\\.[0-9]+' | head -n 1",
                        returnStdout: true
                    ).trim()

                    echo "Current highest semantic version: ${CURRENT_VERSION}"

                    String NEXT_VERSION

                    if (!CURRENT_VERSION) {
                        // First-ever release
                        NEXT_VERSION = "v1.0.0"
                    } else {
                        def parts = CURRENT_VERSION.replace("v", "").split("\\.")
                        def major = parts[0] as int
                        def minor = parts[1] as int
                        def patch = parts[2] as int

                        patch += 1

                        NEXT_VERSION = "v${major}.${minor}.${patch}"
                    }

                    env.SEMVER_TAG = NEXT_VERSION
                    echo "Next semantic version: ${env.SEMVER_TAG}"
                }
            }
        }


        stage('Promote Image & Push to Docker Hub + Tag Git') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                script {
                    // 1) Promote CI image to semantic + latest on Docker Hub
                    sh """
                        echo "Logging into Docker Hub as ${DOCKERHUB_USR}"
                        echo ${DOCKERHUB_PSW} | docker login -u ${DOCKERHUB_USR} --password-stdin

                        echo "Promoting CI image:"
                        echo "  from: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                        echo "  to:   ${DOCKERHUB_USR}/${IMAGE_NAME}:${SEMVER_TAG} and :latest"

                        docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USR}/${IMAGE_NAME}:${SEMVER_TAG}
                        docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKERHUB_USR}/${IMAGE_NAME}:latest

                        docker push ${DOCKERHUB_USR}/${IMAGE_NAME}:${SEMVER_TAG}
                        docker push ${DOCKERHUB_USR}/${IMAGE_NAME}:latest

                        docker logout
                    """

                    // 2) Git tag for version bookkeeping (so next build knows what to bump from)
                    sh """
                        git config --global user.email "jenkins@ci.local"
                        git config --global user.name "Jenkins CI"

                        echo "Creating git tag: ${SEMVER_TAG}"
                        git tag -a ${SEMVER_TAG} -m "Release ${SEMVER_TAG}"

                        echo "Pushing git tag to GitHub..."
                        git push https://${GITHUB_USR}:${GITHUB_PSW}@github.com/thexDman/domain_monitoring_devops.git ${SEMVER_TAG}
                    """
                }
            }
        }

    } // stages

    post {
        failure {
            echo "Tests FAILED — dumping container logs..."
            sh "docker logs ${CONTAINER_NAME} || true"
        }

        always {
            echo "Cleaning temp containers & images..."
            sh """
                docker rm -f ${CONTAINER_NAME} || true
                # If you want more aggressive cleanup, uncomment:
                # docker system prune -af --volumes || true
            """
        }
    }
}
