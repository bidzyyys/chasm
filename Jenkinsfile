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
                sh './build/tests/all_unit_tests --log_level=all --report_level=no --log_format=XML > test_results.xml'
            }
            post {
                always {
                    xunit (
                        thresholds: [ skipped(failureThreshold: '0'), failed(failureThreshold: '0') ],
                        tools: [ BoostTest(pattern: 'test_results.xml') ]
                    )
                }
            }
        }

        stage('Valgrind') {
            steps {  
                sh '''
                    valgrind \
                        --tool=memcheck \
                        --leak-check=full \
                        --show-reachable=yes \
                        --undef-value-errors=yes \
                        --track-origins=yes \
                        --child-silent-after-fork=yes \
                        --trace-children=yes \
                        --gen-suppressions=all \
                        --xml=yes \
                        --xml-file=all_unit_tests.memcheck \
                        --error-exitcode=1 \
                        -v ./build/tests/all_unit_tests
                '''
            }
            post {
                always {
                    publishValgrind (
                      failBuildOnInvalidReports: true,
                      failBuildOnMissingReports: true,
                      failThresholdDefinitelyLost: '',
                      failThresholdInvalidReadWrite: '',
                      failThresholdTotal: '',
                      pattern: '*all_unit_tests.memcheck',
                      publishResultsForAbortedBuilds: false,
                      publishResultsForFailedBuilds: true,
                      sourceSubstitutionPaths: '',
                      unstableThresholdDefinitelyLost: '',
                      unstableThresholdInvalidReadWrite: '',
                      unstableThresholdTotal: ''
                    )
                }
            }
        }

        stage ('CppCheck') {
            steps {
                sh 'cppcheck --enable=all --inconclusive --xml --xml-version=2 `git ls-files "*.hpp" "*.cpp"` 2> cppcheck.xml'
            }
            post {
                always {
                    publishCppcheck pattern:'cppcheck.xml'
                }
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
