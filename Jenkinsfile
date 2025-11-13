pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        VENV_DIR = "${WORKSPACE}/.venv"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip_cache"
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: 'refs/heads/main']],
                    doGenerateSubmoduleConfigurations: false,
                    extensions: [[$class: 'CleanBeforeCheckout']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/C14-2025/Sisdiv.git',
                        credentialsId: 'github-cred'
                    ]]
                ])
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        # Linux/Mac
                        which python3 || which python
                        python3 -m venv "${VENV_DIR}" || python -m venv "${VENV_DIR}"
                        . "${VENV_DIR}/bin/activate"
                        pip install --upgrade pip setuptools wheel
                        mkdir -p "${PIP_CACHE_DIR}"
                        """
                    } else {
                        bat """
                        @echo off
                        python -m venv "${VENV_DIR}"
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        python -m pip install --upgrade pip setuptools wheel
                        if not exist "${PIP_CACHE_DIR}" mkdir "${PIP_CACHE_DIR}"
                        """
                    }
                }
            }
        }

        stage('Generate Documentation') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . "${VENV_DIR}/bin/activate"
                        pip install sphinx
                        if [ -d "docs" ]; then
                            sphinx-build -b html docs/ docs/_build/html
                            echo "Documentation generated"
                        else
                            echo "No documentation source found"
                        fi
                        """
                    } else {
                        bat """
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        python -m pip install sphinx
                        if exist docs (
                            sphinx-build -b html docs/ docs/_build/html
                            echo "Documentation generated"
                        ) else (
                            echo "No documentation source found"
                        )
                        """
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . "${VENV_DIR}/bin/activate"
                        if [ -f "requirements.txt" ]; then
                            pip install --cache-dir="${PIP_CACHE_DIR}" -r requirements.txt
                        else
                            echo "requirements.txt not found"
                        fi
                        """
                    } else {
                        bat """
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        if exist requirements.txt (
                            python -m pip install --cache-dir="${PIP_CACHE_DIR}" -r requirements.txt
                        ) else (
                            echo requirements.txt not found
                        )
                        """
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . "${VENV_DIR}/bin/activate"
                        pip install build
                        python -m build
                        """
                    } else {
                        bat """
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        python -m pip install build
                        python -m build
                        """
                    }
                }
            }
        }

        stage('Integration Tests') {  
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . "${VENV_DIR}/bin/activate"
                        pip install pytest
                        pytest src/tests/test_integration_api.py --maxfail=1 --disable-warnings
                        """
                    } else {
                        bat """
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        python -m pip install pytest
                        python -m pytest src\\tests\\test_integration_api.py --maxfail=1 --disable-warnings
                        """
                    }
                }
            }
        }

        stage('Deploy to Test') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        echo "Deploying build ${env.BUILD_NUMBER} to test environment..."
                        ls -la dist/ 2>/dev/null || echo "No dist directory"
                        """
                    } else {
                        bat """
                        echo "Deploying build ${env.BUILD_NUMBER} to test environment..."
                        dir dist 2>nul || echo No dist directory
                        """
                    }
                }
            }
        }

        stage('Backup Artifacts') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        mkdir -p backups
                        cp -r dist "backups/dist_${env.BUILD_NUMBER}" 2>/dev/null || echo "No artifacts to backup"
                        echo "Backup completed"
                        """
                    } else {
                        bat """
                        if not exist backups mkdir backups
                        xcopy dist "backups\\dist_${env.BUILD_NUMBER}" /E /I /Y 2>nul || echo No artifacts to backup
                        echo Backup completed
                        """
                    }
                }
            }
        }

        stage('Generate Logs') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        . "${VENV_DIR}/bin/activate"
                        mkdir -p logs
                        timeout 20s python src/main.py > logs/main.log 2>&1 || echo "Log generation completed"
                        """
                    } else {
                        bat """
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        if not exist logs mkdir logs
                        start "" /B python src\\main.py > logs\\main.log 2>&1
                        timeout /T 20 >nul
                        taskkill /F /IM python.exe >nul 2>&1
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            node ('mestre') {
                archiveArtifacts artifacts: 'dist/**', fingerprint: true
                archiveArtifacts artifacts: 'logs/**/*.log', fingerprint: true
                archiveArtifacts artifacts: 'backups/**', fingerprint: true

                script {
                    currentBuild.description = "Build #${env.BUILD_NUMBER} - ${currentBuild.result}"
                }
            }
        }
        success {
            echo "Pipeline executada com sucesso!"
            emailext (
                subject: "SUCESSO: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build executado com sucesso!\nURL: ${env.BUILD_URL}",
                to: 'teste@gmail.com'
            )
        }
        failure {
            echo "Pipeline falhou."
            emailext (
                subject: "FALHA: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build falhou!\nVerifique: ${env.BUILD_URL}",
                to: 'tulioalmeida67@gmail.com'
            )
        }
    }
}
