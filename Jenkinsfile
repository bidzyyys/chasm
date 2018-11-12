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

        stage ('Pre-analysis') {
            steps {
                sh 'cppcheck --enable=all --inconclusive --xml --xml-version=2 `git ls-files "*.hpp" "*.cpp"` 2> cppcheck.xml'
                publishCppcheck pattern:'cppcheck.xml'
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
