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
        checkout scm
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          set -e
          python -V
          python -m venv "${VENV_DIR}"
          . "${VENV_DIR}/bin/activate"
          python -m pip install --upgrade pip setuptools wheel
          mkdir -p "${PIP_CACHE_DIR}"
        '''
      }
    }

    stage('Instala dependencias') {
      steps {
        sh '''
          . "${VENV_DIR}/bin/activate"
            pip install --cache-dir="${PIP_CACHE_DIR}" -r requirements.txt
        '''
      }
    }

    stage('Build') {
      steps {
        sh '''
          . "${VENV_DIR}/bin/activate"
          pip install --upgrade build || true
          # run the build (creates dist/)
          python -m build
        '''
      }
      post {
        success {
          echo "Build completada com sucesso."
        }
      }
    }


}