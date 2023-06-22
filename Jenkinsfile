pipeline {
    agent any
    environment {
        AWS_ACCOUNT_ID = "731253471521"
        AWS_DEFAULT_REGION = "us-east-1"
        IMAGE_REPO_NAME = "docker-ecs-repo"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${IMAGE_REPO_NAME}"
        TEMPLATE_FILE = "task-definition-template.json"
        FINAL_FILE = "task-definition.json"
    }

    stages {

        stage('Logging into AWS ECR') {
            steps {
                sh "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
            }
        }

        stage('Cloning Git') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/Rohitkhapre/flask-app.git']]])
            }
        }

        // Building Docker images
        stage('Building image') {
            steps {
                script {
                  sh "docer build --no-cache -t ${IMAGE_REPO_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        // Uploading Docker images to AWS ECR
        stage('Pushing to ECR') {
            steps {
                script {
                    sh "docker tag ${IMAGE_REPO_NAME}:${IMAGE_TAG} ${REPOSITORY_URI}:${IMAGE_TAG}"
                    sh "docker push ${REPOSITORY_URI}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                script {
                    // Set the path of task definition files
                    def templateFile = "${workspace}/${TEMPLATE_FILE}"
                    def finalFile = "${workspace}/${FINAL_FILE}"

                    // Replace the image tag in the template file with the Jenkins variable value
                    sh "cat ${templateFile} | jq '.containerDefinitions[0].image = \"${REPOSITORY_URI}:${IMAGE_TAG}\"' > ${finalFile}"

                    // Register the updated task definition
                    def newTaskDef = sh(
                        script: "aws ecs register-task-definition --cli-input-json file://${finalFile} --query 'taskDefinition.taskDefinitionArn' --output text",
                        returnStdout: true
                        ).trim()

                    // Update the ECS service with the new task definition
                    sh "aws ecs update-service --cluster flask-pipeline-ecs --service ecs-deploy-service --task-definition ${newTaskDef}"
                }
            }
        }
    }
}
