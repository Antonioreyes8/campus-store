````markdown
# Campus Store FastAPI Deployment on EC2 with Docker and ECS

This README documents the full workflow for deploying the **Campus Store FastAPI app** to **AWS**, using **EC2**, **Docker**, **ECS**, and optionally **GitHub Actions** for automated deployment.

---

## Table of Contents

1. [Concepts](#concepts)
2. [EC2 Setup](#ec2-setup)
3. [SSH Key Setup (PEM and GitHub Actions)](#ssh-key-setup-pem-and-github-actions)
4. [App Setup on EC2](#app-setup-on-ec2)
5. [Docker Setup and Running Containers](#docker-setup-and-running-containers)
6. [Scaling Simulation](#scaling-simulation)
7. [ECR: Push Docker Image](#ecr-push-docker-image)
8. [ECS: Cluster, Task, and Service](#ecs-cluster-task-and-service)
9. [GitHub Actions Workflow](#github-actions-workflow)
10. [Testing Deployment](#testing-deployment)
11. [Useful Commands](#useful-commands)

---

## Concepts

- **EC2:** Virtual server to host your application.
- **FastAPI:** Python web framework for building APIs.
- **Uvicorn:** ASGI server for running FastAPI apps.
- **Docker:** Containerization platform for packaging and running your app with all dependencies.
- **ECR:** Amazon Elastic Container Registry to store Docker images.
- **ECS:** Amazon Elastic Container Service for running containers at scale.
- **Systemd service:** Runs app as a background service, restarts automatically.
- **SSH keys:** Secure key-based authentication (no passwords).
- **GitHub Actions:** CI/CD for automated deployments.
- **Auto-scaling / Load Balancing:** Multiple tasks simulate horizontal scaling; optional ALB distributes traffic.

---

## EC2 Setup

1. Launch an EC2 instance (Ubuntu 24.04 LTS recommended).  
2. Ensure **Security Groups** allow:  
   - **SSH (22)**  
   - **HTTP/Custom TCP (8000)** for FastAPI  
3. Obtain **Public IPv4 address**.  
4. Connect via SSH using PEM key:

```bash
ssh -i ~/Downloads/campus-key.pem ubuntu@<EC2_PUBLIC_IP>
````

---

## SSH Key Setup (PEM and GitHub Actions)

### 1. PEM for EC2 SSH

```bash
chmod 400 ~/Downloads/campus-key.pem
ssh -i ~/Downloads/campus-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 2. SSH Key for GitHub Actions

```bash
cd ~/campus_store_app
ssh-keygen -t ed25519 -f github_actions_ec2 -C "github-actions-deploy"
```

Copy public key to EC2:

```bash
mkdir -p ~/.ssh
echo "<contents-of-github_actions_ec2.pub>" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Test SSH:

```bash
ssh -i ~/campus_store_app/github_actions_ec2 ubuntu@<EC2_PUBLIC_IP>
```

---

## App Setup on EC2

```bash
sudo apt update
sudo apt install python3-venv python3-pip git -y
git clone https://github.com/<username>/campus-store.git
cd campus-store
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
ps aux | grep uvicorn
kill <PID>
```

---

## Docker Setup and Running Containers

```bash
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

> ⚠️ Log out and SSH back in to apply Docker group changes.

Build or pull image:

```bash
docker build -t campus-store:latest .
docker run -d -p 8000:8000 campus-store:latest
```

Open browser:

```
http://<EC2_PUBLIC_IP>:8000/docs
```

Optional restart policy:

```bash
docker run -d -p 8000:8000 --restart always campus-store:latest
```

---

## Scaling Simulation

Run multiple containers on the same EC2 to simulate scaling:

```bash
docker run -d -p 8001:8000 campus-store:latest
docker run -d -p 8002:8000 campus-store:latest
```

Optional: add Nginx or ALB to distribute traffic.

---

## ECR: Push Docker Image

1. Create ECR repository: `campus-store`
2. Authenticate Docker to ECR:

```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
```

3. Tag and push image:

```bash
docker tag campus-store:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/campus-store:latest
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/campus-store:latest
```

---

## ECS: Cluster, Task, and Service

### 1. Create ECS Cluster

* ECS → Clusters → Create Cluster → **Fargate only**
* Name: `campus-store-cluster`

### 2. Create Task Definition

* ECS → Task Definitions → Create new → Fargate
* Container:

  * Name: `campus-store`
  * Image: ECR image URL
  * Port mapping: 8000/TCP

### 3. Create ECS Service

* Cluster → campus-store-cluster → Services → Create
* Launch type: Fargate
* Service name: `campus-store-service`
* Number of tasks: 2+
* Optional: enable ALB for load balancing (health check: `/docs`)

> ECS spins up multiple tasks, demonstrating horizontal scaling.

---

## GitHub Actions Workflow

```yaml
name: Deploy to EC2

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3

    - name: Deploy via SSH
      uses: appleboy/ssh-action@v0.1.9
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ubuntu
        key: ${{ secrets.EC2_SSH_KEY }}
        port: 22
        script: |
          cd ~/campus-store
          git reset --hard
          git pull origin main
          source venv/bin/activate
          sudo systemctl restart campus-store
```

---

## Testing Deployment

1. Push test commit → trigger workflow:

```bash
echo "# Test deploy" >> test_deploy.txt
git add test_deploy.txt
git commit -m "Test deploy workflow"
git push origin main
```

2. Check Actions → success
3. SSH → check service or Docker:

```bash
docker ps
sudo systemctl status campus-store
```

4. ECS public endpoint:

```
http://<ALB or task public IP>:8000/docs
```

---

## Useful Commands

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
ps aux | grep uvicorn
kill <PID>
docker ps
docker stop <CONTAINER_ID>
sudo journalctl -u campus-store -f
sudo systemctl daemon-reload
sudo systemctl restart campus-store
ssh -i ~/campus_store_app/github_actions_ec2 ubuntu@<EC2_PUBLIC_IP>
```

---

### Notes

* Deployment changes triggered by `main` branch.
* EC2 can run **systemd service**, **Docker containers**, or ECS tasks.
* Docker ensures portability, ECS ensures scalability.
* Optional ALB distributes traffic and improves availability.
* Keep PEM and GitHub Actions keys secure.
* Running multiple ECS tasks simulates **horizontal scaling**.

---

### Congratulations! 🎉

You now have a **complete, repeatable deployment guide** for:

* EC2 + Docker deployment
* ECS cluster with multiple tasks
* ECR for Docker images
* Optional ALB for load balancing
* GitHub Actions automation
* Scalable FastAPI application

