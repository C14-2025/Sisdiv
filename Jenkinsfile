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
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        # Try python3 first, fallback to python
                        python --version || python3 --version
                        python -m venv "${VENV_DIR}"
                        . "${VENV_DIR}/bin/activate"
                        python -m pip install --upgrade pip setuptools wheel
                        mkdir -p "${PIP_CACHE_DIR}"
                        """
                    } else {
                        bat """
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
                        python -m pip install sphinx || echo "Sphinx installation skipped"
                        if [ -d "docs" ]; then
                            python -m sphinx.cmd.build -b html docs/ docs/_build/html
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
                            python -m pip install --cache-dir="${PIP_CACHE_DIR}" -r requirements.txt
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
                        python -m pip install build
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

        stage('Deploy to Test') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        echo "Deploying build ${env.BUILD_NUMBER} to test environment..."
                        if [ -d "dist" ]; then
                            echo "Artifacts ready for deployment:"
                            ls -la dist/
                        fi
                        """
                    } else {
                        bat """
                        echo "Deploying build ${env.BUILD_NUMBER} to test environment..."
                        if exist dist (
                            echo "Artifacts ready for deployment:"
                            dir dist
                        )
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
                        if [ -d "dist" ]; then
                            cp -r dist "backups/dist_${env.BUILD_NUMBER}"
                            echo "Artifacts backed up to backups/dist_${env.BUILD_NUMBER}"
                        fi
                        """
                    } else {
                        bat """
                        if not exist backups mkdir backups
                        if exist dist (
                            xcopy dist "backups\\dist_${env.BUILD_NUMBER}" /E /I /Y
                            echo "Artifacts backed up to backups\\dist_${env.BUILD_NUMBER}"
                        )
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
                        # Run for 20 seconds and capture logs
                        timeout 20s python src/main.py > logs/main.log 2>&1 || echo "Log generation completed"
                        """
                    } else {
                        bat """
                        call "${VENV_DIR}\\Scripts\\activate.bat"
                        if not exist logs mkdir logs
                        start "" /B python src\\main.py > logs\\main.log 2>&1
                        timeout /T 20
                        taskkill /F /IM python.exe > NUL 2>&1
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dist/**', fingerprint: true
            archiveArtifacts artifacts: 'logs/**/*.log', fingerprint: true
            archiveArtifacts artifacts: 'backups/**', fingerprint: true
            
            script {
                currentBuild.description = "Build #${env.BUILD_NUMBER} - ${currentBuild.result}"
            }
        }
        changed {
            echo "Build status changed from ${currentBuild.previousBuild?.result} to ${currentBuild.result}"
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
                to: 'teste@gmail.com'
            )
        }
    }
}