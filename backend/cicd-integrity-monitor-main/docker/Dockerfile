FROM python:3.12-slim

# Prevent Python buffering issues in GitHub Actions
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy scanner source
COPY scanner /app/scanner
COPY rules /app/rules
COPY policies /app/policies

# Move requirements to the correct location
COPY scanner/requirements.txt /app/requirements.txt

# Install Python requirements
RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

# Default entrypoint for GitHub Action (scanner path + API options)
ENTRYPOINT ["python", "-m", "scanner.scanner.cli"]
