````markdown
# Campus Store FastAPI Deployment on EC2 with GitHub Actions

This README documents the full workflow for deploying the **Campus Store FastAPI app** to an **AWS EC2 instance**, automatically updating from **GitHub** using **GitHub Actions**.

---

## Table of Contents

1. [Concepts](#concepts)
2. [EC2 Setup](#ec2-setup)
3. [App Setup on EC2](#app-setup-on-ec2)
4. [Systemd Service for Automatic Startup](#systemd-service-for-automatic-startup)
5. [SSH Keys for GitHub Actions](#ssh-keys-for-github-actions)
6. [GitHub Actions Workflow](#github-actions-workflow)
7. [Testing Deployment](#testing-deployment)
8. [Useful Commands](#useful-commands)

---

## Concepts

- **EC2**: Virtual server from AWS to host your application.
- **FastAPI**: Python web framework for building APIs.
- **Uvicorn**: ASGI server for running FastAPI.
- **Systemd service**: Manages app as a background service, starts on boot, restarts automatically.
- **SSH keys**: Public/private key pairs used for secure authentication without passwords.
- **GitHub Actions**: CI/CD service that automates deployment on push to `main`.
- **Workflow**: YAML file in `.github/workflows` directory defining automated tasks.

---

## EC2 Setup

1. Launch an EC2 instance (Ubuntu 24.04 LTS recommended).
2. Make sure **port 8000** is allowed in **Security Groups** for HTTP access.
3. Connect via SSH using your PEM key:
   ```bash
   ssh -i ~/Downloads/campus-key.pem ubuntu@<EC2_PUBLIC_IP>
````

---

## App Setup on EC2

1. Install required packages:

   ```bash
   sudo apt update
   sudo apt install python3-venv python3-pip git -y
   ```

2. Clone your repo (if not already cloned):

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

5. Stop manual server before systemd setup:

   ```bash
   ps aux | grep uvicorn
   kill <PID>
   ```

---

## Systemd Service for Automatic Startup

1. Create a service file:

   ```bash
   sudo nano /etc/systemd/system/campus-store.service
   ```

2. Add the following content:

   ```ini
   [Unit]
   Description=Campus Store FastAPI
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/campus-store
   ExecStart=/home/ubuntu/campus-store/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Reload systemd and enable service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable campus-store
   sudo systemctl start campus-store
   ```

4. Check status:

   ```bash
   sudo systemctl status campus-store
   ```

---

## SSH Keys for GitHub Actions

1. Generate a key pair on your local machine:

   ```bash
   cd ~/campus_store_app
   ssh-keygen -t ed25519 -f github_actions_ec2 -C "github-actions-deploy"
   ```

2. Copy the **public key** to the EC2 instance:

   ```bash
   # On EC2:
   mkdir -p ~/.ssh
   echo "<public-key-from-github_actions_ec2.pub>" >> ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

3. Test SSH from your local machine:

   ```bash
   ssh -i ~/campus_store_app/github_actions_ec2 ubuntu@<EC2_PUBLIC_IP>
   ```

> ✅ This allows GitHub Actions to SSH into your EC2 securely for deployments.

---

## GitHub Actions Workflow

1. Create a `.github/workflows/deploy.yml` file:

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

   * `EC2_HOST` → EC2 public IP
   * `EC2_SSH_KEY` → Private key from `github_actions_ec2` (copy content of file)

---

## Testing Deployment

1. Make a small change locally:

   ```bash
   echo "# Test deploy" >> test_deploy.txt
   git add test_deploy.txt
   git commit -m "Test deploy workflow"
   git push origin main
   ```

2. Go to **GitHub Actions** → verify workflow runs successfully.

3. Check EC2:

   ```bash
   ssh -i ~/campus_store_app/github_actions_ec2 ubuntu@<EC2_PUBLIC_IP>
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

* Check systemd service logs:

  ```bash
  sudo journalctl -u campus-store -f
  ```

* Reload systemd services after changes:

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
* EC2 runs your app as a **systemd service**, ensuring it stays alive even after reboots.
* GitHub Actions securely connects via the SSH key and pulls the latest code.
* Keep your private key (`github_actions_ec2`) secure.

---

```

---