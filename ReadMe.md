# Campus Store FastAPI Deployment on EC2 with GitHub Actions

This README documents the full workflow for deploying the **Campus Store FastAPI app** to an **AWS EC2 instance**, using **Docker** and optionally **GitHub Actions** for automated deployment.

---

## Table of Contents

1. [Concepts](#concepts)
2. [EC2 Setup](#ec2-setup)
3. [SSH Key Setup (PEM and GitHub Actions)](#ssh-key-setup-pem-and-github-actions)
4. [App Setup on EC2](#app-setup-on-ec2)
5. [Docker Setup and Running Containers](#docker-setup-and-running-containers)
6. [Scaling Simulation](#scaling-simulation)
7. [GitHub Actions Workflow](#github-actions-workflow)
8. [Testing Deployment](#testing-deployment)
9. [Useful Commands](#useful-commands)

---

## Concepts

- **EC2:** Virtual server from AWS to host your application.
- **FastAPI:** Python web framework for building APIs.
- **Uvicorn:** ASGI server for running FastAPI apps.
- **Docker:** Containerization platform for packaging and running your app with all dependencies.
- **Systemd service:** Manages your app as a background service, restarts on failure or reboot.
- **SSH keys:** Secure key-based authentication (no passwords).
- **GitHub Actions:** CI/CD service to automate deployments on push to `main`.
- **Auto-scaling / Load Balancing:** Optional simulation using multiple container instances.

---

## EC2 Setup

1. Launch an EC2 instance (Ubuntu 24.04 LTS recommended).
2. Ensure **Security Groups** allow:
   - **SSH (22)**
   - **HTTP/Custom TCP (8000)** for FastAPI access
3. Obtain the **Public IPv4 address** of your instance.
4. Connect via SSH using your PEM key (replace path and IP):

```bash
ssh -i ~/Downloads/campus-key.pem ubuntu@<EC2_PUBLIC_IP>
````

---

## SSH Key Setup (PEM and GitHub Actions)

### 1. Using PEM for EC2 SSH

* Make sure permissions are secure:

```bash
chmod 400 ~/Downloads/campus-key.pem
```

* SSH into EC2:

```bash
ssh -i ~/Downloads/campus-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 2. SSH Key for GitHub Actions

* Generate a key for automated deploys:

```bash
cd ~/campus_store_app
ssh-keygen -t ed25519 -f github_actions_ec2 -C "github-actions-deploy"
```

* Copy the **public key** to EC2:

```bash
mkdir -p ~/.ssh
echo "<contents-of-github_actions_ec2.pub>" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

* Test SSH from local machine:

```bash
ssh -i ~/campus_store_app/github_actions_ec2 ubuntu@<EC2_PUBLIC_IP>
```

---

## App Setup on EC2

1. Update packages and install Python and Git:

```bash
sudo apt update
sudo apt install python3-venv python3-pip git -y
```

2. Clone your repository:

```bash
git clone https://github.com/<username>/campus-store.git
cd campus-store
```

3. Set up Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Test app manually with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5. Stop manual server before systemd or Docker setup:

```bash
ps aux | grep uvicorn
kill <PID>
```

---

## Docker Setup and Running Containers

1. Install Docker:

```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

> ⚠️ Log out and SSH back in to apply group changes.

2. Build Docker image locally (optional) or pull from Docker Hub:

```bash
docker pull YOUR_USERNAME/campus-store:latest
```

3. Run container on EC2:

```bash
docker run -d -p 8000:8000 YOUR_USERNAME/campus-store:latest
```

4. Open in browser:

```
http://<EC2_PUBLIC_IP>:8000
http://<EC2_PUBLIC_IP>:8000/docs
```

5. Optional: run container with restart policy:

```bash
docker run -d -p 8000:8000 --restart always YOUR_USERNAME/campus-store:latest
```

---

## Scaling Simulation

* Run multiple containers on same EC2 to simulate horizontal scaling:

```bash
docker run -d -p 8001:8000 YOUR_USERNAME/campus-store:latest
docker run -d -p 8002:8000 YOUR_USERNAME/campus-store:latest
```

* Optional: Use a load balancer (Nginx or AWS ALB) to distribute traffic to multiple container ports.

---

## GitHub Actions Workflow

1. Create `.github/workflows/deploy.yml`:

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

2. Add GitHub secrets:

* `EC2_HOST` → Public IP of EC2
* `EC2_SSH_KEY` → Private key content of `github_actions_ec2`

---

## Testing Deployment

1. Push a test commit to trigger workflow:

```bash
echo "# Test deploy" >> test_deploy.txt
git add test_deploy.txt
git commit -m "Test deploy workflow"
git push origin main
```

2. Check GitHub Actions → workflow success.
3. SSH into EC2 and verify systemd or Docker:

```bash
docker ps
sudo systemctl status campus-store
```

---

## Useful Commands

* Start app manually:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

* Stop running Uvicorn process:

```bash
ps aux | grep uvicorn
kill <PID>
```

* Check Docker containers:

```bash
docker ps
```

* Stop Docker container:

```bash
docker stop <CONTAINER_ID>
```

* Check logs for systemd service:

```bash
sudo journalctl -u campus-store -f
```

* Reload systemd after changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart campus-store
```

* Test SSH manually:

```bash
ssh -i ~/campus_store_app/github_actions_ec2 ubuntu@<EC2_PUBLIC_IP>
```

---

### Notes

* All deployment changes are triggered by pushing to `main`.
* EC2 runs your app as a **systemd service** or inside **Docker**, ensuring persistence across reboots.
* Docker enables **portability** and easy **scaling**, while systemd ensures reliability for single-instance setups.
* Keep private keys (`PEM` or `github_actions_ec2`) secure — never commit them to GitHub.
* Simulate multiple instances with Docker to test scaling if auto-scaling groups aren’t used.


### Congratulations! 🎉

You now have a **fully documented, repeatable setup** for:

* EC2 deployment
* Docker containerization
* Virtual environments
* GitHub Actions automated deployment
* Optional scaling and managed database integration

```