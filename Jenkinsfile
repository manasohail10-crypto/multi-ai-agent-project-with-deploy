pipeline {
    agent any

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