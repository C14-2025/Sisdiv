pipeline {
    agent any  // ← DEIXA ASSIM MESMO!

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        VENV_DIR = "${WORKSPACE}\\.venv"
        PIP_CACHE_DIR = "${WORKSPACE}\\.pip_cache"
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
                bat """
                python -m venv "%VENV_DIR%"
                call "%VENV_DIR%\\Scripts\\activate.bat"
                python -m pip install --upgrade pip setuptools wheel
                if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"
                """
            }
        }

        // SEUS NOVOS STAGES AQUI!
        stage('Generate Documentation') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"
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

        stage('Instala Dependencias') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"
                if exist requirements.txt (
                    python -m pip install --cache-dir="%PIP_CACHE_DIR%" -r requirements.txt
                ) else (
                    echo Arquivo requirements.txt não encontrado.
                )
                """
            }
        }

        stage('Build') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"
                python -m pip install --upgrade build
                python -m build
                """
            }
        }

        stage('Deploy to Test') {
            steps {
                bat """
                echo "Deploying build ${env.BUILD_NUMBER} to test environment..."
                if exist dist\\*.* (
                    echo "Artifacts ready for deployment:"
                    dir "dist"
                )
                """
            }
        }

        stage('Backup Artifacts') {
            steps {
                bat """
                if not exist "backups" mkdir "backups"
                if exist "dist\\*.*" (
                    xcopy "dist" "backups\\dist_${env.BUILD_NUMBER}" /E /I /Y
                    echo "Artifacts backed up to backups\\dist_${env.BUILD_NUMBER}"
                )
                """
            }
        }

        stage('Generate Logs') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"
                if not exist logs mkdir logs
                start "" /B python src\\main.py > logs\\main.log 2>&1
                timeout /T 20
                taskkill /F /IM python.exe > NUL 2>&1
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dist/**', fingerprint: true
            archiveArtifacts artifacts: 'logs/**/*.log', fingerprint: true
            archiveArtifacts artifacts: 'backups/**', fingerprint: true
        }
        success {
            echo "Pipeline bem-sucedida"
            emailext (
                subject: "Build Sucesso: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Olá!

                    O pipeline '${env.JOB_NAME}' foi executado com sucesso no build #${env.BUILD_NUMBER}.
                    Veja os detalhes em: ${env.BUILD_URL}

                    Abraços,
                    Jenkins
                """,
                to: 'tulioalmeida67@gmail.com'
            )
        }
        failure {
            echo "Pipeline falhou."
            emailext (
                subject: "Build Falhou: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Atenção!

                    O pipeline '${env.JOB_NAME}' falhou no build #${env.BUILD_NUMBER}.
                    Verifique os logs em: ${env.BUILD_URL}

                    Jenkins
                """,
                to: 'tulioalmeida67@gmail.com'
            )
        }
    }
}
