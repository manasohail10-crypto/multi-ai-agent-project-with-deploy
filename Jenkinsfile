pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = 'multi-ai-agent'
        SONAR_SCANNER_HOME = tool 'Sonarqube'
        AWS_REGION = 'ap-southeast-2'
        ECR_REPO = 'multi-ai-agent'
        IMAGE_TAG = 'latest'
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

        stage('Build and Push Docker Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        def accountId = sh(
                            script: "aws sts get-caller-identity --region ${env.AWS_REGION} --query Account --output text",
                            returnStdout: true
                        ).trim()
                        def registry = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"
                        def ecrUrl = "${registry}/${env.ECR_REPO}"

                        sh """
                        aws ecr get-login-password --region ${env.AWS_REGION} | docker login --username AWS --password-stdin ${registry}
                        docker build -t ${env.ECR_REPO}:${env.IMAGE_TAG} .
                        docker tag ${env.ECR_REPO}:${env.IMAGE_TAG} ${ecrUrl}:${env.IMAGE_TAG}
                        docker push ${ecrUrl}:${env.IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Show images') {
            steps {
                sh 'docker images | head -n 5'
            }
        }
    }
}