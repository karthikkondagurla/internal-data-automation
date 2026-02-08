# AWS EC2 Deployment Guide

This guide details how to deploy the `internal-data-automation` project to an AWS EC2 instance using Docker.

## Prerequisites
- AWS Account
- Terminal with SSH client
- Git

## Part 1: EC2 Setup

1.  **Launch Instance**:
    - Go to AWS Console > EC2 > Instances > Launch Instances.
    - **Name**: `internal-data-automation-prod`
    - **OS Image**: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type.
    - **Instance Type**: `t2.micro` or `t3.micro` (Free tier eligible).
    - **Key Pair**: Create new key pair (e.g., `prod-key.pem`). Download and save it securely.

2.  **Network Settings**:
    - **Security Group**: Create a new security group.
    - **Inbound Rules**:
        - Type: SSH (TCP 22)
        - Source: My IP (Restrict access to your current IP address for security).

3.  **Launch**: Click "Launch Instance".

4.  **Connect**:
    - Locate your key file (`prod-key.pem`).
    - Set permissions (Linux/Mac): `chmod 400 prod-key.pem`.
    - Connect via SSH:
      ```bash
      ssh -i "path/to/prod-key.pem" ubuntu@<your-ec2-public-ip>
      ```

## Part 2: Server Bootstrap

Once connected to the EC2 instance, install Docker:

1.  **Update System**:
    ```bash
    sudo apt-get update && sudo apt-get upgrade -y
    ```

2.  **Install Docker**:
    ```bash
    sudo apt-get install -y docker.io
    ```

3.  **Start & Enable Docker**:
    ```bash
    sudo systemctl start docker
    sudo systemctl enable docker
    ```

4.  **Configure User Permissions**:
    Add the `ubuntu` user to the `docker` group to run docker without sudo.
    ```bash
    sudo usermod -aG docker ubuntu
    ```
    **Log out and log back in** for this to take effect.

5.  **Verify Installation**:
    ```bash
    docker --version
    docker run hello-world
    ```

## Part 3: Deploy Application

1.  **Clone Repository**:
    ```bash
    git clone https://github.com/karthikkondagurla/internal-data-automation.git
    cd internal-data-automation
    ```

2.  **Build Docker Image**:
    ```bash
    docker build -t internal-data-automation .
    ```

3.  **Create Production Directories**:
    Create persistent directories on the host machine.
    ```bash
    sudo mkdir -p /opt/internal-data-automation/data
    sudo mkdir -p /opt/internal-data-automation/logs
    sudo mkdir -p /opt/internal-data-automation/reports
    
    # Change ownership to ubuntu user so we can manage them easily
    sudo chown -R ubuntu:ubuntu /opt/internal-data-automation
    ```

4.  **Prepare Environment Variables**:
    Create a `.env` file on the server.
    ```bash
    nano .env
    ```
    Paste your **REAL** production keys:
    ```bash
    ALPHA_VANTAGE_API_KEY=your_real_key
    NEWS_API_KEY=your_real_key
    ```
    Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

5.  **Run Container**:
    Run the container in the background (detached mode) with restart policy.
    
    *Note: Since this is a pipeline script that runs once and exits, using `restart: always` might cause it to loop indefinitely if the script finishes quickly. For a daily job, you typically use `cron` on the host to run `docker run`. However, per instructions to keep container running or restart on failure:*

    **Option A: One-off Run (Manual)**
    ```bash
    docker run --rm \
      --env-file .env \
      -v /opt/internal-data-automation/data:/app/data \
      -v /opt/internal-data-automation/reports:/app/reports \
      -v /opt/internal-data-automation/logs:/app/logs \
      internal-data-automation
    ```

    **Option B: Scheduled Job (Recommended for Production)**
    Add to crontab (`crontab -e`) to run daily at 8 AM:
    ```bash
    0 8 * * * docker run --rm --env-file /home/ubuntu/internal-data-automation/.env -v /opt/internal-data-automation/data:/app/data -v /opt/internal-data-automation/reports:/app/reports -v /opt/internal-data-automation/logs:/app/logs internal-data-automation
    ```

## Part 4: Operations

- **Check Running Containers**:
  ```bash
  docker ps
  ```

- **View Logs (Last Run)**:
  ```bash
  cat /opt/internal-data-automation/logs/pipeline.log
  ```

- **Manually Trigger Pipeline**:
  Run the `docker run` command from Option A above.

- **Stop Container** (if stuck):
  ```bash
  docker stop <container-id>
  ```

## Part 5: Validation

1.  **Check Logs**:
    Ensure the log file ends with "Pipeline run <uuid> marked SUCCESS".
    ```bash
    tail -n 20 /opt/internal-data-automation/logs/pipeline.log
    ```

2.  **Verify Data Persistence**:
    Check if the SQLite database exists and is growing.
    ```bash
    ls -l /opt/internal-data-automation/data/internal_data.db
    ```

3.  **Inspect Audit Trail**:
    You can inspect the SQLite DB directly on the host using `sqlite3` (install with `sudo apt install sqlite3`).
    ```bash
    sqlite3 /opt/internal-data-automation/data/internal_data.db "SELECT * FROM pipeline_runs ORDER BY started_at DESC LIMIT 5;"
    ```

## Security Best Practices
- **Never commit `.env` to GitHub**.
- **Restrict SSH access**: Only allow your IP in the Security Group.
- **Backups**: Periodically back up the `/opt/internal-data-automation/data` directory (e.g., to S3).
