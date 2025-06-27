# Manufacturing Machine Efficiency Prediction

A machine learning application that predicts manufacturing machine efficiency status based on various operational parameters. The system uses advanced ML algorithms to classify machine efficiency into three categories: High, Medium, and Low efficiency.

## 🎯 Project Overview

This project provides an end-to-end solution for predicting manufacturing machine efficiency using:
- **Data Processing Pipeline**: Automated data cleaning, feature engineering, and preprocessing
- **Machine Learning Model**: Logistic Regression classifier for efficiency prediction
- **Web Application**: Interactive Flask-based interface for real-time predictions

## 📊 Features

- **Multi-parameter Analysis**: Processes 14 different machine parameters including:
  - Operation Mode (Idle, Active, Maintenance)
  - Temperature, Vibration, Power Consumption
  - Network metrics (Latency, Packet Loss)
  - Quality Control metrics
  - Production Speed and Error Rates
  - Temporal features (Year, Month, Day, Hour)

- **Real-time Predictions**: Web interface for instant efficiency predictions
- **Model Confidence**: Provides prediction confidence scores
- **Scalable Architecture**: Modular design for easy maintenance and updates

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository** (or download the project files)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

## 🌩️ Cloud Deployment Setup (GCP VM with CI/CD Pipeline)

This section provides a complete guide to deploy the application on Google Cloud Platform with a full CI/CD pipeline using Jenkins, Docker, Kubernetes (Minikube), and ArgoCD.

### 🖥️ GCP VM Instance Setup

#### 1. Create GCP VM Instance

1. **Navigate to Google Cloud Console** → Compute Engine → VM Instances
2. **Click "Create Instance"**
3. **Configure the instance**:
   - **Region**: Choose a region nearby for better performance
   - **Machine Type**: e2-standard-4 (16 GB RAM)
   - **Boot Disk**: Ubuntu 22.04 LTS (x86/64)
   - **Storage**: 128 GB
   - **Networking**: 
     - ✅ Allow HTTP traffic
     - ✅ Allow HTTPS traffic 
     - ✅ Allow load balancer health checks
     - ✅ Enable IP forwarding
4. **Click "Create"**

#### 2. Initial VM Setup

Once the VM is created, connect via SSH (opens in Google Cloud Shell):

> **Note**: All commands in this section should be run in the **VM SSH terminal**

```bash
# Update system packages
sudo apt update

# Install Git
sudo apt install git

# Clone your project repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### 🐳 Docker Installation

> **Note**: Run these commands in the **VM SSH terminal**

```bash
# Add Docker's official GPG key
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Test Docker installation
sudo docker run hello-world

# Add user to docker group (to avoid using sudo)
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Test without sudo
docker run hello-world

# Configure Docker to start on boot
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

# Verify Docker status
systemctl status docker

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a
```

> **Note**: To stop Docker if needed: `sudo systemctl disable docker.service` and `sudo systemctl disable containerd.service`

### ☸️ Kubernetes (Minikube) Setup

> **Note**: Run these commands in the **VM SSH terminal**

```bash
# Install Minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64

# Start Minikube
minikube start

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Optional: Verify kubectl download
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check

# Install kubectl
sudo snap install kubectl --classic

# Verify installation
kubectl version --client
kubectl version --client --output=yaml

# Check Minikube status
minikube status

# Navigate to your cloned repository
cd YOUR_CLONED_REPO_NAME

# Verify nodes
kubectl get nodes

# Check cluster info
kubectl cluster-info

# Check running containers
docker ps

# Check all Docker networks
docker network ls
```

> **Note**: Make sure Jenkins and Minikube use the same network (we'll configure this in Jenkins setup)

### 🔧 Jenkins Setup

#### 1. Setup Jenkins with Docker-in-Docker

> **Note**: Run these commands in the **VM SSH terminal**

```bash
# Setup Jenkins container with Docker access (using minikube network)
docker run -d --name jenkins \
-p 8080:8080 \
-p 50000:50000 \
-v /var/run/docker.sock:/var/run/docker.sock \
-v $(which docker):/usr/bin/docker \
-u root \
-e DOCKER_GID=$(getent group docker | cut -d: -f3) \
--network minikube \
jenkins/jenkins:lts

# Check if Jenkins container is running
docker ps

# Get Jenkins initial admin password
docker logs jenkins
```

> **Note**: Copy the password from the logs output

#### 2. Configure Firewall Rules

**Create a firewall rule to access Jenkins:**

1. **Go to VPC Network** → **Firewall** → **Create Firewall Rule**
2. **Configuration**:
   - **Name**: `allow-jenkins`
   - **Logs**: Off
   - **Network**: Default
   - **Priority**: 1000
   - **Direction**: Ingress
   - **Action**: Allow
   - **Targets**: All instances in the network
   - **Source filter**: IPv4 ranges
   - **Source IPv4 ranges**: `0.0.0.0/0`
   - **Second source filter**: None
   - **Destination filter**: None
   - **Protocols and ports**: Allow all

> **Note**: We're allowing all protocols and ports because we'll use ArgoCD later. You can be more specific for better security.

#### 3. Jenkins Initial Setup

1. **Access Jenkins**: `http://YOUR_VM_EXTERNAL_IP:8080`
2. **Enter the admin password** from `docker logs jenkins`
3. **Install suggested plugins**
4. **Create admin user** and remember the credentials
5. **Click "Start using Jenkins"**
6. **Dismiss security warning**: You may see "Building on the built-in node can be a security issue" - you can dismiss it
7. **Install additional plugins**:
   - Go to **Jenkins Dashboard** → **Manage Jenkins** → **Plugins**
   - Search for and select **"Docker"** - install both:
     - `Docker`
     - `Docker Pipeline`
   - Search for and select **"Kubernetes"**
   - Click **"Install"**
   - Scroll down and verify all three plugins installed successfully

#### 4. Restart Jenkins

> **Note**: Run this command in the **VM SSH terminal**

```bash
docker restart jenkins
```

- Refresh the Jenkins web UI and wait for it to finish starting
- Login again with your credentials

#### 5. Configure Jenkins Environment

> **Note**: Run these commands in the **VM SSH terminal**

```bash
# Install Python in Jenkins container
docker exec -it jenkins bash
apt update -y
apt install -y python3
python3 --version
# Make python3 as python command
ln -s /usr/bin/python3 /usr/bin/python
python --version
apt install -y python3-pip
apt install -y python3-venv
exit

# Restart Jenkins to apply changes
docker restart jenkins
```

- Refresh the Jenkins web UI and wait for it to finish starting
- Login again with your credentials

### 🔑 GitHub Integration

#### 1. Create GitHub Personal Access Token

1. **GitHub** → **Profile Settings** → **Developer settings** → **Personal access tokens**
2. **Generate new token (classic)** with permissions:
   - `repo`
   - `workflow` 
   - `admin:org`
   - `admin:public_key`
   - `admin:repo_hook`
   - `admin:org_hook`
3. **Copy the token** and keep it (or keep the webpage open)

#### 2. Add GitHub Credentials to Jenkins

1. **Jenkins Dashboard** → **Manage Jenkins** → **Credentials**
2. **Global** → **Add Credentials**:
   - **Scope**: Keep same (Global)
   - **Kind**: Username with password
   - **Username**: Your GitHub username
   - **Password**: GitHub personal access token (paste the token)
   - **ID**: `github-token`
   - **Description**: `github-token` (or your own description)

### 📝 Jenkins Pipeline Configuration

#### 1. Create Jenkins Pipeline

1. **Jenkins Dashboard** → **New Item**
2. **Enter name** (e.g., "GITOPS") → **Pipeline** → **OK**
3. **Pipeline Configuration**:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your GitHub repository URL
   - **Credentials**: `github-token` (select the one we just created)
   - **Branch**: `main` (or your working branch)
4. **Click Apply** → **Save**

#### 2. Generate Checkout Pipeline Script

1. **Pipeline Syntax**: Click "Pipeline Syntax" link
2. **Sample Step**: Select `checkout: Check out from version control`
3. **Configuration**:
   - **SCM**: Git
   - **Repository URL**: Your GitHub repository (same as above)
   - **Credentials**: `github-token`
   - **Branch**: `main`
4. **Generate Pipeline Script**: Click "Generate Pipeline Script"
5. **Copy the script** - you'll need it in Jenkinsfile

#### 3. Create Jenkinsfile

> **Note**: Create this on your **local machine** in project folder, then push to GitHub

Create a Jenkinsfile with the following structure (replace the checkout line with your generated script):

```jenkinsfile
pipeline {
    agent any
    stages {
        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
                // Replace this line with your generated checkout script
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/YOUR_USERNAME/YOUR_REPO_NAME']])
            }
        }        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
            }
        }
        stage('Push Image to DockerHub') {
            steps {
                echo 'Pushing Docker image to DockerHub...'
            }
        }
        stage('Install Kubectl & ArgoCD CLI') {
            steps {
                echo 'Installing Kubectl and ArgoCD CLI...'
            }
        }
        stage('Apply Kubernetes & Sync App with ArgoCD') {
            steps {
                echo 'Applying Kubernetes and syncing with ArgoCD...'
            }
        }
    }
}
```

> **Note**: Change the checkout line completely with your pipeline script. Just change the credentialId and GitHub URL.

#### 4. Commit and Push Jenkinsfile

**Option 1: On Local Machine**
```bash
# Add, commit and push the Jenkinsfile
git add .
git commit -m "Add Jenkinsfile"
git push origin main
```

**Option 2: Create directly on VM**
```bash
# Navigate to your project folder in VM SSH
cd YOUR_CLONED_REPO_NAME

# Install vim if needed
sudo apt update && sudo apt install vim

# Create Jenkinsfile using vim
vi Jenkinsfile
# Paste your pipeline content, then press ESC, type :wq! and press Enter

# Configure git (replace with your details)
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"

# Commit and push
git add .
git commit -m "Jenkinsfile added"
git push origin main
# Enter your GitHub username when prompted
# Enter your GitHub personal access token as password (it won't show while typing)
```

### 🐳 DockerHub Integration

> **Note**: Pull from GitHub repo first: `git pull origin main`

#### 1. Create DockerHub Repository

1. **Go to DockerHub** → Create account if you don't have one and sign in
2. **Create repository**: Name it (e.g., `gitops-project`) → Add description if any → Keep public → Click create

#### 2. Generate DockerHub Access Token

1. **Profile** → **Account Settings** → **Security** → **New Access Token**
2. **Configuration**:
   - **Access token description**: Give any name
   - **Access permissions**: Read, Write, Delete
   - **Expiration**: Select expiration date
3. **Generate** → Copy the token and keep it (also keep your DockerHub username)

#### 3. Add DockerHub Credentials to Jenkins

1. **Jenkins Dashboard** → **Manage Jenkins** → **Credentials**
2. **Global** → **Add Credentials**:
   - **Kind**: Username with password
   - **Username**: Your DockerHub username
   - **Password**: DockerHub access token (paste the token)
   - **ID**: `gitops-dockerhub-token`
   - **Description**: `gitops-dockerhub-token`
   - **Create**

### 📋 Update Project Files

#### 1. Update manifests/deployment.yaml

Update line 17 in `manifests/deployment.yaml` with your DockerHub repository:
```yaml
image: YOUR_DOCKERHUB_USERNAME/gitops-project:latest
```
Example: `image: avnishsingh17/gitops-project:latest`

#### 2. Update Jenkinsfile Environment

Add environment variables to your Jenkinsfile (between `agent any` and `stages`):

```jenkinsfile
pipeline {
    agent any
    environment {
        DOCKER_HUB_REPO = "YOUR_DOCKERHUB_USERNAME/gitops-project"
        DOCKER_HUB_CREDENTIALS_ID = "gitops-dockerhub-token"
    }
    stages {
        // ... existing stages
    }
}
```

> **Note**: Make sure you use the correct repo name and credential ID that we created in Jenkins for DockerHub.

#### 3. Update Jenkinsfile Build and Push Stages

Replace the build and push stages with:

```jenkinsfile
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
            docker.withRegistry('https://registry.hub.docker.com', "${DOCKER_HUB_CREDENTIALS_ID}") {
                dockerImage.push('latest')
            }
        }
    }
}
```

#### 4. Commit and Push Changes

```bash
git add .
git commit -m "image push and build added in jenkinsfile"
git push origin main
# or just: git push
```

#### 5. Test Jenkins Pipeline

1. **Check your GitHub repo** - Jenkinsfile should be updated
2. **Go to Jenkins UI Dashboard** → Select your pipeline → **Build Now**
3. **Check Console Output** - should successfully build and push to DockerHub
4. **Check DockerHub repo** - should have the built image

> **Note**: If there are any errors, check if you followed the steps properly

### 🚀 ArgoCD Installation and Setup

> **Note**: Run these commands in the **VM SSH terminal**

#### 1. Create ArgoCD Namespace

```bash
# Check existing namespaces
kubectl get namespace

# Create new namespace for ArgoCD
kubectl create ns argocd

# Verify namespace creation
kubectl get namespace
# Should show 'argocd' now
```

#### 2. Install ArgoCD

```bash
# Install ArgoCD through kubectl
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Check all pods are running (wait for all to be in Running state)
kubectl get all -n argocd

# Check services for 'argocd' namespace
kubectl get svc -n argocd
```

> **Note**: You'll see 'argocd-server' is ClusterIP. We need to convert this to NodePort because ClusterIP can only be accessed internally, while NodePort can be accessed externally.

#### 3. Convert ArgoCD Server to NodePort

```bash
# Edit the argocd-server service
kubectl edit svc argocd-server -n argocd
```

**In the editor:**
1. **Find**: `type: ClusterIP`
2. **Replace with**: `type: NodePort` # you might need to press 'i' to enter insert mode and use delete button to delete 'ClusterIP'
3. **Save**: Press `ESC` → type `:wq!` → press `Enter`
4. **Verify**: Should show `service/argocd-server edited`

```bash
# Verify the change
kubectl get svc -n argocd
```

**Expected output:**
```
argocd-server    NodePort    10.105.79.8    <none>    80:31416/TCP,443:30749/TCP   14m
```

#### 4. Port Forward ArgoCD

> **Note**: Use the correct port from your argocd-server (in example above, it's 30749)

```bash
# Port forward (replace 30749 with your port)
kubectl port-forward --address 0.0.0.0 service/argocd-server 30749:80 -n argocd
```

**This will show**: `Forwarding from 0.0.0.0:30749 -> 8080`

> **Important**: Keep this terminal running! Don't close the port-forward command as it handles the ArgoCD UI connection.

#### 5. Access ArgoCD UI

1. **Open browser**: `http://YOUR_VM_EXTERNAL_IP:30749` (use your port number)
2. **Security warning**: "Connection is not private" → Click **Advanced** → **Continue to site**
3. **Login credentials**:
   - **Username**: `admin`
   - **Password**: Get from next step

#### 6. Get ArgoCD Admin Password

> **Note**: Open a **new VM SSH terminal** (don't close the port-forward terminal)

```bash
# Navigate to your project
cd YOUR_CLONED_REPO_NAME

# Get the admin password (make sure namespace is correct)
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Copy the base64 password** and use it to login to ArgoCD UI

### 🚀 Quick Summary: Terminal Management

During the setup, you'll need to manage multiple VM SSH terminals simultaneously:

- **Terminal 1**: ArgoCD port-forward (must stay running for ArgoCD UI access)
- **Terminal 2**: Commands for getting passwords, configurations, etc.  
- **Terminal 3**: Minikube tunnel (must stay running for app access)
- **Terminal 4**: Application port-forward (must stay running for app access)

> **Important**: Never close terminals running port-forward or tunnel commands, as this will make the services inaccessible.

### ⚙️ Kubernetes Configuration Setup

> **Note**: Navigate to root if you're in project folder in VM SSH terminal

```bash
# Navigate to root directory
cd ..
ls -lah
```

You will find `.kube` folder. Let's work with the config file:

```bash
# Check files in .kube folder
ls -la .kube

# Display the config content
cat .kube/config
```

#### 1. Setup Kubeconfig for Jenkins

**Copy the config content** and paste it in notepad on your **local machine**.

**Modify the copied content:**
1. **Inside** `clusters: - cluster:` **section**, change:
   - `certificate-authority` → `certificate-authority-data`
   - `client-certificate` → `client-certificate-data`  
   - `client-key` → `client-key-data`

2. **Get base64 encoded certificate values** (run in VM SSH):

```bash
# Get CA certificate base64 - user full path from config paste content of values of key 'certificate-authority', 'client-certificate' and 'client-key'
cat /home/USERNAME/.minikube/ca.crt | base64 -w 0; echo

# Get client certificate base64  
cat /home/USERNAME/.minikube/profiles/minikube/client.crt | base64 -w 0; echo

# Get client key base64
cat /home/USERNAME/.minikube/profiles/minikube/client.key | base64 -w 0; echo
```

3. **Replace file paths with base64 content** in your notepad:
   - Replace `/home/USERNAME/.minikube/ca.crt` path with first base64 output
   - Replace `/home/USERNAME/.minikube/profiles/minikube/client.crt` path with second base64 output
   - Replace `/home/USERNAME/.minikube/profiles/minikube/client.key` path with third base64 output

#### 2. Create Kubeconfig File

> **Note**: Do this on your **local machine**

**Open Git Bash** (install Git if not installed locally):
1. **Switch to clean directory** or create new (you can delete it after we create the files)
2. **Create kubeconfig file**:
   ```bash
   vi kubeconfig
   ```
3. **Paste the modified content** from notepad with `-data` keys and base64 values [whole content that copied earlier from cat .kube/config]
4. **Save and exit**: Press `ESC` → type `:wq!` → press `Enter`
5. **Verify creation**: Check in file explorer - make sure it has no file extension, just `kubeconfig`

#### 3. Upload Kubeconfig to Jenkins

1. **Jenkins Dashboard** → **Manage Jenkins** → **Credentials** → **Global**
2. **Add Credentials**:
   - **Kind**: Secret file
   - **File**: Choose and upload the `kubeconfig` file
   - **ID**: `kubeconfig`
   - **Description**: `kubeconfig`
   - **Create**

> **Note**: When uploaded, it should show name as `kubeconfig` with no extension. If it shows extension, create one without extension.

#### 4. Generate Kubeconfig Pipeline Script

1. **Jenkins Dashboard** → Your pipeline → **Configure**
2. **Pipeline Syntax**: Look for "Pipeline Syntax" link (below Script path Jenkinsfile) → Click it
3. **New tab opens** → **Sample Step**: Search for `kubeconfig: Setup Kubernetes CLI(kubectl)` → Select it
4. **Configuration**:
   - **Kubernetes server endpoint**: 
     ```bash
     # Run in VM SSH to get endpoint
     kubectl cluster-info
     ```
     Copy the URL (e.g., `https://192.168.49.2:8443`) and paste in "Kubernetes server endpoint"
   - **Certificate of certificate authority**: Leave empty
   - **Credential**: Select `kubeconfig`
5. **Generate Pipeline Script**: Click "Generate Pipeline Script"
6. **Copy the script** and keep it separately - we'll use it later

#### 5. Update Jenkinsfile - Install Kubectl & ArgoCD CLI Stage

Update the `Install Kubectl & ArgoCD CLI` stage in Jenkinsfile:

```jenkinsfile
stage('Install Kubectl & ArgoCD CLI') {
    steps {
        sh '''
        echo 'Installing Kubectl and ArgoCD CLI...'
        echo 'installing Kubectl & ArgoCD cli...'
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        mv kubectl /usr/local/bin/kubectl
        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /usr/local/bin/argocd
        '''
    }
}
```

#### 6. Add ArgoCD Credentials to Jenkins

**Add these as Secret Text credentials:**

1. **Jenkins** → **Manage Jenkins** → **Credentials** → **Global** → **Add Credentials**
2. **Kind**: Secret text → Add both credentials:

**ARGOCD_SERVER:**
- **Secret**: `YOUR_VM_EXTERNAL_IP:30749` (replace with your VM IP and ArgoCD port)
- **ID**: `ARGOCD_SERVER`

**KUBE_SERVER_URL:**
- **Secret**: Use `kubectl cluster-info` output (e.g., `https://192.168.49.2:8443`)
- **ID**: `KUBE_SERVER_URL`

#### 7. Update Jenkinsfile Environment Variables

Add the ArgoCD credentials to your Jenkinsfile environment section:

```jenkinsfile
pipeline {
    agent any
    environment {
        DOCKER_HUB_REPO = "YOUR_DOCKERHUB_USERNAME/gitops-project"
        DOCKER_HUB_CREDENTIALS_ID = "gitops-dockerhub-token"
        ARGOCD_SERVER = credentials('ARGOCD_SERVER')
        KUBE_SERVER_URL = credentials('KUBE_SERVER_URL')
    }
    stages {
        // ... existing stages
    }
}
```

#### 8. Update Apply Kubernetes & Sync App with ArgoCD Stage

Replace the `Apply Kubernetes & Sync App with ArgoCD` stage with the kubeconfig pipeline script we generated earlier:

```jenkinsfile
stage('Apply Kubernetes & Sync App with ArgoCD') {
    steps {
        script {
            kubeconfig(credentialsId: 'kubeconfig', serverUrl: "${KUBE_SERVER_URL}") {
                sh """
                argocd login $ARGOCD_SERVER --username admin --password \$(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
                argocd app sync gitopsapp
                """
            }
        }
    }
}
```

> **Important**: We need to use the same name `gitopsapp` when we create the ArgoCD app.

### 🔗 ArgoCD Application Setup

#### 1. Access ArgoCD UI

> **Note**: Make sure the port-forward terminal is still running. If you closed it, run again:

```bash
kubectl port-forward --address 0.0.0.0 service/argocd-server 30749:80 -n argocd
```

**Don't close this terminal** - it provides the ArgoCD web interface.

#### 2. Login to ArgoCD

1. **Go to**: `http://YOUR_VM_EXTERNAL_IP:30749`
2. **Login**: Use the same method as before
   - **Username**: `admin`
   - **Password**: Get from command:
     ```bash
     cd YOUR_REPO_NAME
     kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
     ```

> **Note**: Make sure your namespace is correct (in this case `argocd` namespace)

#### 3. Connect Repository to ArgoCD

1. **ArgoCD UI** → **Settings** (left sidebar) → **Repositories** → **Connect Repo**
2. **Configuration**:
   - **Choose your connection method**: Via HTTPS
   - **Type**: Git
   - **Name**: Give any name (optional)
   - **Project**: Default
   - **Repository URL**: Copy your GitHub project URL (e.g., `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git`) and paste it
   - **Username**: Your choice (optional)
   - **Password**: GitHub token we created earlier
   - **Rest are not required to fill**
3. **Click "CONNECT"** → Should show "Successful"

#### 4. Create ArgoCD Application

1. **ArgoCD UI** → **Applications** → **NEW APP**
2. **Configuration**:
   - **Application name**: `gitopsapp` (must be same as used in Jenkinsfile `argocd app sync gitopsapp`)
   - **Project name**: `default`
   - **Sync policy**: `Automatic`
   - **Options**: ✅ Select **Prune resources** and **Self Heal**
   - **Source**:
     - **Repository URL**: Select the one we just connected
     - **Revision**: Type `main`
     - **Path**: `manifests` (since it has deployment files)
   - **Destination**:
     - **Cluster URL**: Select the default
     - **Namespace**: `argocd` (the namespace we created and are using)
3. **Click "CREATE"** → It will take some time, wait until it shows **HEALTHY**

### 🌐 Application Access Setup

#### 1. Push Code Changes and Test Pipeline

> **Note**: Push code from local machine for the changes we made in Jenkinsfile

```bash
git add .
git commit -m "Updated Jenkinsfile with ArgoCD sync"
git push origin main
```

1. **Go to Jenkins Dashboard** → Your pipeline → **Build Now**
2. **Wait for completion** → Should show success message in console output
3. **Check ArgoCD UI** → The app we created → The pods should be running

#### 2. Setup Application Access

> **Note**: Run these commands in **separate VM SSH terminals** (keep both running)

**Terminal 1: Enable Minikube Tunnel**
```bash
# This command must keep running for internal access
minikube tunnel
```

> **Important**: Don't close this terminal! The tunnel allows internal access to services.

**Terminal 2: Port Forward Application Service**
```bash
# Navigate to your project folder
cd YOUR_REPO_NAME

# Make sure both ArgoCD port-forward and minikube tunnel terminals are running

# Port forward your application service (replace 'my-service' with your actual service name)
kubectl port-forward svc/my-service -n argocd --address 0.0.0.0 9090:80
```

> **Note**: `my-service` is the name of service from `manifests/service.yaml`. Check your service.yaml file for the correct service name.

#### 3. Access Your Application

- **Application URL**: `http://YOUR_VM_EXTERNAL_IP:9090`
- **Jenkins Dashboard**: `http://YOUR_VM_EXTERNAL_IP:8080`
- **ArgoCD Dashboard**: `http://YOUR_VM_EXTERNAL_IP:30749` (or your ArgoCD port)

### 🔄 Webhook Setup for Auto-Deployment

#### 1. Configure GitHub Webhook

> **Note**: Until now we had to manually go to Jenkins dashboard and click "Build Now" to trigger the pipeline. With webhooks, any code push will automatically trigger the build.

1. **Go to your GitHub project repository** → **Settings** → **Webhooks** → **Add webhook**
2. **Configuration**:
   - **Payload URL**: `http://YOUR_VM_EXTERNAL_IP:8080/github-webhook/`
   - **Content type**: `application/json`
   - **SSL verification**: ✅ Enable SSL verification
   - **Which events**: **Just the push event** (default)
   - **Active**: ✅ (should be checked by default)
3. **Click "Add webhook"**

#### 2. Enable Jenkins Webhook Trigger

1. **Jenkins Dashboard** → Your pipeline → **Configure**
2. **Scroll down to "Build Triggers"** → ✅ Tick **"GitHub hook trigger for GITScm polling"**
3. **Apply** → **Save** (don't make any other changes)

#### 3. Test Auto-Deployment

1. **Make some changes** in Jenkinsfile (e.g., change stage name or echo statement)
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Test webhook trigger"
   git push origin main
   ```
3. **Check Jenkins Dashboard** → The build should be automatically triggered without manually clicking "Build Now"

### 🔒 Security Notes

- Replace all placeholder values with your actual configuration
- Keep access tokens and passwords secure
- Use proper firewall rules in production
- Consider using service accounts instead of personal tokens
- Regularly rotate access tokens and passwords

### 🚀 Complete Deployment Summary

Your full CI/CD pipeline is now complete! Here's what happens automatically:

1. **Code Push** → GitHub webhook triggers Jenkins
2. **Jenkins** → Builds Docker image and pushes to DockerHub
3. **Jenkins** → Syncs with ArgoCD using kubectl
4. **ArgoCD** → Automatically deploys to Kubernetes cluster
5. **Application** → Accessible via minikube tunnel and port-forwarding

### 📋 Terminal Management Summary

You should now have these terminals running simultaneously:

- **Terminal 1**: ArgoCD port-forward (`kubectl port-forward --address 0.0.0.0 service/argocd-server 30749:80 -n argocd`)
- **Terminal 2**: Minikube tunnel (`minikube tunnel`)  
- **Terminal 3**: Application port-forward (`kubectl port-forward svc/SERVICE_NAME -n argocd --address 0.0.0.0 9090:80`)
- **Terminal 4**: General commands (free to use)

> **Critical**: Keep terminals 1, 2, and 3 running for full system access. Closing any of these will make the respective services inaccessible.

### ⚙️ Troubleshooting Jenkins Pipeline Issues

1. **Pipeline fails to checkout code**:
   - Ensure GitHub credentials are correct in Jenkins
   - Check if the repository URL and branch are correct in the pipeline configuration

2. **Docker image build or push fails**:
   - Verify DockerHub credentials in Jenkins
   - Ensure the Docker daemon is running and accessible
   - Check Jenkins logs for detailed error messages

3. **Kubernetes deployment or ArgoCD sync fails**:
   - Ensure kubectl and ArgoCD CLI are correctly installed in Jenkins
   - Verify the kubeconfig file is correctly set up and accessible
   - Check if the ArgoCD server is reachable from Jenkins

4. **General tips**:
   - Always check the console output of the Jenkins pipeline for specific error messages
   - Ensure all services (Docker, Kubernetes, ArgoCD) are running and accessible
   - Verify network settings, firewall rules, and security groups in GCP

## 📁 Project Structure

```
manufacturing_machine_efficiency_prediction/
├── app.py                          # Flask web application
├── Dockerfile                     # Docker container configuration
├── Jenkinsfile                    # Jenkins CI/CD pipeline definition
├── requirements.txt               # Python dependencies
├── setup.py                      # Package setup configuration
├── pipeline/
│   ├── __init__.py
│   └── training_pipeline.py      # Main training pipeline
├── src/
│   ├── __init__.py
│   ├── data_processing.py         # Data preprocessing utilities
│   ├── model_training.py          # Model training and evaluation
│   ├── logger.py                  # Logging configuration
│   └── custom_exception.py        # Custom exception handling
├── artifacts/
│   ├── raw/
│   │   └── data.csv              # Raw training data
│   ├── processed/                # Processed data files
│   │   ├── X_train.pkl
│   │   ├── X_test.pkl
│   │   ├── y_train.pkl
│   │   ├── y_test.pkl
│   │   └── scaler.pkl
│   └── models/
│       └── model.pkl             # Trained model
├── manifests/                     # Kubernetes deployment files
│   ├── deployment.yaml           # Kubernetes deployment configuration
│   └── service.yaml              # Kubernetes service configuration
├── templates/
│   └── index.html                # Web interface template
├── static/
│   └── style.css                 # Web interface styling
└── logs/
    └── log_*.log                 # Application logs
```

### Key CI/CD Files

- **Dockerfile**: Containerizes the Flask application for deployment
- **Jenkinsfile**: Defines the complete CI/CD pipeline with stages for:
  - GitHub checkout
  - Docker image building
  - DockerHub image pushing
  - kubectl & ArgoCD CLI installation
  - Kubernetes deployment and ArgoCD synchronization
- **manifests/deployment.yaml**: Kubernetes deployment with DockerHub image reference
- **manifests/service.yaml**: Kubernetes service for application access

## 🔧 Usage

### Web Interface

1. **Access the Application**: Open your browser and navigate to `http://localhost:5000`

2. **Input Parameters**: Fill in the machine parameters:
   - **Operation Mode**: Select from Idle, Active, or Maintenance
   - **Environmental**: Temperature (°C), Vibration (Hz)
   - **Performance**: Power Consumption (kW), Production Speed (units/hr)
   - **Quality**: Defect Rate (%), Error Rate (%)
   - **Network**: Latency (ms), Packet Loss (%)
   - **Maintenance**: Predictive Maintenance Score (0-1)
   - **Temporal**: Year, Month, Day, Hour

3. **Get Prediction**: Click "Predict Efficiency" to get:
   - Efficiency Status (High/Medium/Low)
   - Prediction Confidence Score

### API Endpoint

For programmatic access, use the `/predict` endpoint:

```python
import requests
import json

data = {
    "Operation_Mode": 1,
    "Temperature_C": 65.5,
    "Vibration_Hz": 2.5,
    "Power_Consumption_kW": 7.2,
    "Network_Latency_ms": 25.3,
    "Packet_Loss_%": 1.5,
    "Quality_Control_Defect_Rate_%": 3.2,
    "Production_Speed_units_per_hr": 350,
    "Predictive_Maintenance_Score": 0.75,
    "Error_Rate_%": 2.1,
    "Year": 2024,
    "Month": 6,
    "Day": 15,
    "Hour": 14
}

response = requests.post("http://localhost:5000/predict", json=data)
result = response.json()
print(f"Efficiency: {result['prediction']}, Confidence: {result['confidence']}")
```

## 🧠 Model Details

### Algorithm
- **Model Type**: Logistic Regression
- **Features**: 14 engineered features
- **Target Classes**: 3 efficiency levels (High=0, Low=1, Medium=2)
- **Preprocessing**: StandardScaler normalization

### Performance Metrics
The model is evaluated using:
- Accuracy Score
- Precision (weighted average)
- Recall (weighted average)
- F1 Score (weighted average)

### Data Processing Pipeline

1. **Data Loading**: Reads CSV data with timestamp parsing
2. **Feature Engineering**:
   - Extracts temporal features (Year, Month, Day, Hour)
   - Categorical encoding for Operation_Mode and Efficiency_Status
   - Removes unnecessary columns (Timestamp, Machine_ID)
3. **Preprocessing**:
   - Standard scaling for numerical features
   - Train-test split (80-20) with stratification
4. **Model Training**: Logistic Regression with hyperparameters
5. **Evaluation**: Comprehensive metrics calculation

## 📈 Input Parameters Reference

| Parameter | Range | Unit | Description |
|-----------|-------|------|-------------|
| Operation_Mode | 0-2 | - | 0=Idle, 1=Active, 2=Maintenance |
| Temperature_C | 20-100 | °C | Operating temperature |
| Vibration_Hz | 0-5 | Hz | Machine vibration frequency |
| Power_Consumption_kW | 0-15 | kW | Power consumption |
| Network_Latency_ms | 0-50 | ms | Network communication latency |
| Packet_Loss_% | 0-5 | % | Network packet loss rate |
| Quality_Control_Defect_Rate_% | 0-10 | % | Product defect rate |
| Production_Speed_units_per_hr | 50-500 | units/hr | Production speed |
| Predictive_Maintenance_Score | 0-1 | - | Maintenance prediction score |
| Error_Rate_% | 0-15 | % | System error rate |
| Year | 2020-2030 | - | Year |
| Month | 1-12 | - | Month |
| Day | 1-31 | - | Day |
| Hour | 0-23 | - | Hour (24-hour format) |

## 🔍 Output Categories

- **High Efficiency**: Optimal machine performance
- **Medium Efficiency**: Moderate performance, may need attention
- **Low Efficiency**: Poor performance, requires immediate action

## 🛠️ Development

### Adding New Features

1. Update the feature list in `src/data_processing.py`
2. Modify the preprocessing pipeline if needed
3. Update the web interface forms in `templates/index.html`
4. Retrain the model with new features

### Customizing the Model

1. Edit `src/model_training.py` to use different algorithms
2. Adjust hyperparameters as needed
3. Update evaluation metrics if required

## 📝 Logging

The application includes comprehensive logging:
- **Location**: `logs/` directory
- **Format**: Daily log files (`log_YYYY-MM-DD.log`)
- **Levels**: INFO, ERROR, DEBUG
- **Coverage**: Data processing, model training, predictions


## 🆘 Troubleshooting

### Common Issues

1. **Module Import Errors**: Ensure you've installed the package with `pip install -e .`
2. **Missing Data**: Verify `artifacts/raw/data.csv` exists before training
3. **Model Not Found**: Run the training pipeline before starting the web app
4. **Port Already in Use**: Change the port in `app.py` or stop conflicting services

