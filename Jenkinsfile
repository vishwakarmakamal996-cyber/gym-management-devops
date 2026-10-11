pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        IMAGE_NAME = "gym-management-api:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install dependencies') {
            steps {
                sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt'
            }
        }
        stage('Test') {
            steps {
                sh '. .venv/bin/activate && pytest -q'
            }
        }
        stage('Build image') {
            steps {
                sh 'docker build -t "$IMAGE_NAME" .'
            }
        }
        stage('Trivy OS scan') {
            steps {
                sh 'trivy image --pkg-types os --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed "$IMAGE_NAME"'
            }
        }
        stage('Trivy dependency scan') {
            steps {
                sh 'trivy fs --scanners vuln --pkg-types library --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed requirements.txt'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker compose up -d --build'
            }
        }
    }

    post {
        always {
            sh 'docker image rm "$IMAGE_NAME" || true'
        }
    }
}
