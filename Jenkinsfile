pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'mkdir -p build'
            }
        }
        stage('Build') {
            steps {
                sh '''
                   cd build &&
                   cmake -D CMAKE_BUILD_TYPE=Debug -D BUILD_TESTING=ON .. &&
                   make
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                   cd build &&
                   ctest -R all
                '''
            }
        }
        stage('Coverage') {
            steps{
                sh 'echo Coverage'
            }
        }
        stage('Linter'){
            steps{
                sh 'echo Linter'
            }
        }
    }
    post {
        success {
            slackSend color: "good", message: "Job: ${env.JOB_NAME} with build number ${env.BUILD_NUMBER} was successful"
        }
        failure {
           slackSend color: "danger", message: "Job: ${env.JOB_NAME} with build number ${env.BUILD_NUMBER} was failed"
        }
        unstable {
            slackSend color: "warning", message: "Job: ${env.JOB_NAME} with build number ${env.BUILD_NUMBER} was unstable"
        }
        changed {
           slackSend color: "warning", message: "Job: ${env.JOB_NAME} with build number ${env.BUILD_NUMBER} its result has changed state of the pipeline"
        }
    }
}
