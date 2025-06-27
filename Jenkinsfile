pipeline {
    agent any
    environment {
    DOCKER_HUB_REPO = "avnishsingh17/gitops-project"
    DOCKER_HUB_CREDENTIALS_ID = "gitops-dockerhub-token"
    ARGOCD_SERVER = credentials('ARGOCD_SERVER')
    KUBE_SERVER_URL = credentials('KUBE_SERVER_URL')
    }
    stages {
        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
		checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/avnishs17/manufacturing_machine_efficiency_prediction']])
		    }
        }        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:latest")
                }
            }
        }
        stage('Push Image to DockerHub') {
            steps {
                script {
                    echo 'Pushing Docker image to DockerHub...'
                    docker.withRegistry('https://registry.hub.docker.com' , "${DOCKER_HUB_CREDENTIALS_ID}") {
                        dockerImage.push('latest')
                    }
                }
            }
        }
        stage('Install Kubectl & ArgoCD CLI') {
            steps {
                sh'''
                echo 'installing Kubectl & ArgoCD cli...'
                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                chmod +x kubectl
                mv kubectl /usr/local/bin/kubectl
                curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
                chmod +x /usr/local/bin/argocd
                '''
            }
        }
        stage('Apply Kubernetes & Sync App with ArgoCD trigger check') {
            steps {
                script {
                    kubeconfig(credentialsId: 'kubeconfig', serverUrl: "${KUBE_SERVER_URL}") {
                        sh '''
                        argocd login $ARGOCD_SERVER --username admin --password \$(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
                        argocd app sync gitopsapp
                        '''
                    }
                }
            }
        }
    }
}
