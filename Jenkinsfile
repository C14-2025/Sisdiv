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

        stage('Clean Workspace & Checkout') {
            steps {
                // Wipe old workspace to get latest pyproject.toml etc.
                deleteDir()

                // Checkout main branch with credentials
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

        stage('Install Dependencies') {
            steps {
                bat """
                call "%VENV_DIR%\\Scripts\\activate.bat"

                REM Install dependencies if requirements.txt exists
                if exist requirements.txt (
                    pip install --cache-dir="%PIP_CACHE_DIR%" -r requirements.txt
                )
                """
            }
        }

        stage('Build Package') {
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
    }

    // Top-level post block
    post {
        always {
            archiveArtifacts artifacts: 'dist/**', fingerprint: true
        }
        success {
            echo "Pipeline bem-sucedida\\"
        }
        failure {
            echo "Pipeline falhou."
        }
    }
}
