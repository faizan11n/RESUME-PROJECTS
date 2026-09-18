pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        IMAGE_NAME = 'faizan1112002/notesapp-web'
        IMAGE_TAG = "v${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                // Pulls the latest code from GitHub using the stored credentials
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/faizan11n/RESUME-PROJECTS.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('project-1-cicd-pipeline') {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker push ${IMAGE_NAME}:latest"
            }
        }

        stage('Deploy Container') {
            steps {
                dir('project-1-cicd-pipeline') {
                    // Restart the app with the freshly built image, keeping the database untouched
                    sh "docker compose up -d --build webapp"
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully! Deployed ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline failed. Check the logs above for details."
        }
    }
}
