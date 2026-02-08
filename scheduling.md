# Scheduling Guide

This guide explains how to automate the daily execution of the `internal-data-automation` pipeline on AWS EC2.

## Overview

We use `cron` on the host EC2 instance to trigger the Docker container. Idempotency is handled by the wrapper script `scripts/run_pipeline_prod.sh`, which uses a lock file to prevent overlapping runs.

## 1. Prerequisites

- SSH into your EC2 instance.
- Ensure the project is deployed at `~/internal-data-automation`.
- Ensure production directories exist (`/opt/internal-data-automation/...`).
- Ensure `.env` is present at `~/internal-data-automation/.env`.

## 2. Install the Script

1.  Capabilities: Copy the script to a executable location or keep it in the repo.
    ```bash
    cp ~/internal-data-automation/scripts/run_pipeline_prod.sh ~/run_pipeline_prod.sh
    chmod +x ~/run_pipeline_prod.sh
    ```

## 3. Configure Cron

1.  Open the crontab for the `ubuntu` user:
    ```bash
    crontab -e
    ```

2.  Add the following line to run daily at **6:00 AM UTC**:
    ```bash
    # Run Internal Data Automation Pipeline Daily at 06:00 UTC
    0 6 * * * /home/ubuntu/run_pipeline_prod.sh >> /opt/internal-data-automation/logs/cron.log 2>&1
    ```

3.  Save and exit.

## 4. Verification

To verify the schedule works:

1.  **Check Cron Logs**:
    ```bash
    grep CRON /var/log/syslog
    ```

2.  **Check Pipeline Logs**:
    The script logs its own execution details to:
    `/opt/internal-data-automation/logs/cron_run_<DATE>.log`
    
    And the application logs go to:
    `/opt/internal-data-automation/logs/pipeline.log`

## 5. Disabling Schedule

To pause the automation temporarily (e.g., for maintenance):

1.  Comment out the line in crontab:
    ```bash
    crontab -e
    # 0 6 * * * ...
    ```

## AWS EventBridge (Future)
This architecture is checking forward-compatible with AWS EventBridge (formerly CloudWatch Events). If you migrate to ECS (Elastic Container Service) or AWS Batch:
- You can trigger the same Docker image using an EventBridge Schedule.
- The entry point (`run_pipeline.py`) is already stateless and idempotent-safe per run ID.
