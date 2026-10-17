pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = 'multi-ai-agent'
        SONAR_SCANNER_HOME = tool 'Sonarqube'
    }

    stages {
        stage('Clone GitHub repo') {
            steps {
                echo 'Cloning GitHub repo to Jenkins............'
                checkout scmGit(
                    branches: [[name: '*/master']],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: 'github-token',
                        url: 'https://github.com/manasohail10-crypto/multi-ai-agent-project-with-deploy.git'
                    ]]
                )
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    withSonarQubeEnv('Sonarqube') {
                        sh '''
                        $SONAR_SCANNER_HOME/bin/sonar-scanner \
                          -Dsonar.projectKey=$SONAR_PROJECT_KEY \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=http://sonarqube-dind:9000 \
                          -Dsonar.token=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker --version'
                sh 'docker build -t multi-ai-agent:jenkins .'
            }
        }

        stage('Show images') {
            steps {
                sh 'docker images | head -n 5'
            }
        }
    }
}