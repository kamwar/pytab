pipeline {
  agent any
  stages {
    stage('run') {
      parallel {
        stage('unit_test') {
          steps {
            sh './docker/dock-run pytest --alluredir=./allure-results --junitxml=./unit_test_report.xml test_demo.py'
          }
        }
        stage('flake8') {
          steps {
            sh './docker/dock-run touch ./flake8_report.xml'
            sh './docker/dock-run sh -c "git rev-parse HEAD^^^ | xargs git diff | flake8 --diff  --show-source --format junit-xml --output-file ./flake8_report.xml"'
          }
        }
      }
    }
  }
  post {
    always {
      allure([[path: 'allure-results']])
      junit 'unit_test_report.xml'
      junit 'flake8_report.xml'

    }
  }
}
