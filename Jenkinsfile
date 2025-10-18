pipeline {
    agent any

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
                REM Create virtual environment
                python -m venv "%VENV_DIR%"
                call "%VENV_DIR%\\Scripts\\activate.bat"

                REM Upgrade pip/setuptools/wheel
                python -m pip install --upgrade pip setuptools wheel

                REM Prepare pip cache
                if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"
                """
            }
        }

        stage('Instala Dependencias') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"

                REM Install dependencies if requirements.txt exists
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

                REM Ensure build module is installed
                python -m pip install --upgrade build

                REM Build sdist + wheel
                python -m build
                """
            }
        }

        stage('Generate Logs') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"

                REM create logs directory if it does not exists
                if not exist logs mkdir logs

                REM Execute application for 20 seconds and saves the output
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
                to: 'teste@gmail.com'
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
                to: 'teste@gmail.com'
            )
        }
    }
}