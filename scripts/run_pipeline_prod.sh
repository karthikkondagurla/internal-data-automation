#!/bin/bash
# ==============================================================================
# Internal Data Automation - Production Pipeline Runner
# ==============================================================================
# Usage: ./run_pipeline_prod.sh
# 
# This script is designed to be run via Cron on the EC2 instance.
# It ensures idempotency using a lock file and runs the Docker container
# with production settings.
# ==============================================================================

# Configuration
LOCK_FILE="/tmp/internal-data-automation.lock"
LOG_DIR="/opt/internal-data-automation/logs"
DATE=$(date +%Y-%m-%d)
RUN_LOG_FILE="${LOG_DIR}/cron_run_${DATE}.log"
ENV_FILE="/home/ubuntu/internal-data-automation/.env"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Logging Function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "${RUN_LOG_FILE}"
}

# 1. Acquire Lock
# Use flock to ensure only one instance runs at a time.
# If lock is held, exit immediately (fail-safe for overlapping runs).
exec 200>"${LOCK_FILE}"
flock -n 200 || {
    log "ERROR: Another instance is already running. Exiting."
    exit 1
}

log "Starting Production Pipeline Run..."

# 2. Check for .env file
if [ ! -f "${ENV_FILE}" ]; then
    log "ERROR: .env file not found at ${ENV_FILE}. Exiting."
    exit 1
fi

# 3. Pull latest image (optional, if you use a registry)
# docker pull your-registry/internal-data-automation:latest

# 4. Run Docker Container
# - --rm: Clean up container after exit
# - --env-file: Pass secrets securely
# - -v: Mount persistent directories
# - run_pipeline.py: The entry point (default CMD in Dockerfile)
log "Executing Docker container..."

docker run --rm \
  --env-file "${ENV_FILE}" \
  -v /opt/internal-data-automation/data:/app/data \
  -v /opt/internal-data-automation/reports:/app/reports \
  -v /opt/internal-data-automation/logs:/app/logs \
  internal-data-automation

EXIT_CODE=$?

# 5. Handle Result
if [ $EXIT_CODE -eq 0 ]; then
    log "Pipeline completed SUCCESSFULLY."
else
    log "Pipeline FAILED with exit code ${EXIT_CODE}. Check container logs."
    # Trigger alert here if needed (e.g., SNS, PagerDuty integration)
fi

# Release lock (automatic on exit, but explicit close is good practice)
flock -u 200

exit $EXIT_CODE
