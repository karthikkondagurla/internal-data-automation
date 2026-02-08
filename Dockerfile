# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --group appuser

# Install system dependencies (if any needed, none strict for now but good practice)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy only requirements to cache them in docker layer
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Create directories for data, logs, and reports if they don't exist (and ensure user can write)
# Since we switched user, we need to make sure these exist/are writable. 
# Better pattern: create them as root before switching user.
USER root
RUN mkdir -p data/raw logs reports && \
    chown -R appuser:appgroup data logs reports
USER appuser

# Run the pipeline
CMD ["python", "run_pipeline.py"]
