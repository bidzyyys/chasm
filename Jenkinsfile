pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    environment {
      PATH="/var/jenkins_home/miniconda3/bin/:$PATH"
    }

    stages {
        stage ("Code pull"){
            steps{
                checkout scm
            }
        }
        stage('Build environment') {
            steps {
                echo "Building virtualenv"
                sh  ''' conda create --yes -n ${BUILD_TAG} python
                        source activate ${BUILD_TAG}
                        pip install --upgrade pip
                        pip install -r requirements/dev.txt
                    '''
            }
        }
        stage('Tests') {
            steps {
                sh  ''' source activate ${BUILD_TAG}
                        pytest --cov=chasm
                    '''
            }
        }
        stage('Code style') {
            steps{
                echo "Checking code style"
                sh  ''' source activate ${BUILD_TAG}
                        pylint --disable=C,R -f parseable chasm/ tests/ > pylint.out
                    '''
            }
            post{
                always{
                    step([$class: 'WarningsPublisher',
                            parserConfigurations: [[
                                parserName: 'PyLint',
                                pattern: 'pylint.out'
                            ]],
                            unstableTotalAll: '0',
                            usePreviousBuildAsReference: true
                    ])
                }
            }
        }

        stage('Code metrics') {
            steps {
                echo "Test coverage"
                sh  ''' source activate ${BUILD_TAG}
                        coverage run chasm/chasm.py
                        python -m coverage xml -o reports/coverage.xml
                    '''
            }
            post{
                success{
                    step([$class: 'CoberturaPublisher',
                                   autoUpdateHealth: false,
                                   autoUpdateStability: false,
                                   coberturaReportFile: 'reports/coverage.xml',
                                   failNoReports: false,
                                   failUnhealthy: false,
                                   failUnstable: false,
                                   maxNumberOfBuilds: 10,
                                   onlyStable: false,
                                   sourceEncoding: 'ASCII',
                                   zoomCoverageChart: false])
                }
            }
        }
    }
    post {
        always {
            sh 'conda remove --yes -n ${BUILD_TAG} --all'
        }
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
