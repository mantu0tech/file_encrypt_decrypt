pipeline {
  agent any

  environment {
    AWS_REGION     = 'us-east-1'
    AWS_ACCOUNT_ID = '324352301517'
    ECR_REPOSITORY = 'devops-task'

    IMAGE_TAG    = "${env.BUILD_NUMBER}"
    ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    FULL_IMAGE   = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
    LATEST_IMAGE = "${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '10'))
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
  }

  stages {

    stage('Checkout') {
      steps {
        cleanWs()
        checkout scm
      }
    }

    // ── KILL SWITCH 1 ──
    stage('Gitleaks Scan') {
      steps {
        script {
          def result = sh(returnStatus: true, script: """
            docker run --rm \
              -v ${WORKSPACE}:/path \
              zricethezav/gitleaks:latest \
              detect --source /path \
              --report-format json \
              --report-path /path/gitleaks-report.json \
              --exit-code 1 --no-git
          """)
          archiveArtifacts 'gitleaks-report.json'
          if (result != 0) {
            error("KILL SWITCH: Secrets detected!")
          }
        }
      }
    }

    // ── KILL SWITCH 2 ──
    stage('SonarQube Scan') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh """
            ${tool 'SonarScanner'}/bin/sonar-scanner \
              -Dsonar.projectKey=my-app \
              -Dsonar.sources=.
          """
        }
      }
    }

  

    stage('Docker Build') {
      steps {
        sh """
          docker build --no-cache \
            -t ${FULL_IMAGE} \
            -t ${LATEST_IMAGE} .
        """
      }
    }

    // ── KILL SWITCH 3 ──
    stage('Trivy Scan') {
  steps {
    script {
      sh """
        docker run --rm \
          -v /var/run/docker.sock:/var/run/docker.sock \
          -v ${WORKSPACE}:/workspace \
          ghcr.io/aquasecurity/trivy:0.53.0 image \
          --exit-code 0 \
          --severity HIGH,CRITICAL \
          --format json \
          --output /workspace/trivy-report.json \
          ${FULL_IMAGE}
      """

      archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
    }
  }
}

    stage('Push to ECR') {
      steps {
          sh """
            aws ecr get-login-password --region ${AWS_REGION} | \
            docker login --username AWS --password-stdin ${ECR_REGISTRY}

            aws ecr describe-repositories \
              --repository-names ${ECR_REPOSITORY} \
              --region ${AWS_REGION} || 
            docker push ${FULL_IMAGE}
            docker push ${LATEST_IMAGE}
          """
        }
      }
    

    //  DEPLOYMENT (Jenkins Server)
    stage('Deploy on Server') {
      steps {
        sh """
          docker build -t my-app .
          echo "Stopping old container if exists..."
          docker stop my-app || true
          docker rm my-app || true

          echo "Running new container..."
          docker run -d \
            --name my-app \
            --network monitoring || true \
            --restart unless-stopped \
            -p 5000:5000 \
            ${LATEST_IMAGE}

          echo "Deployment complete"
          docker ps | grep my-app
        """
      }
    }
  }

  post {
    success {
      echo "BUILD SUCCESS: App deployed on Jenkins server"
    }
    failure {
      echo "BUILD FAILED"
    }
    always {
      sh """
        docker rmi ${FULL_IMAGE} || true
        docker rmi ${LATEST_IMAGE} || true
      """
      cleanWs()
    }
  }
}
