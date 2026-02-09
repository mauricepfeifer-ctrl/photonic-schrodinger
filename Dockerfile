FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (if exists, else just install common libs)
# We'll install common libs directly here to be sure
# COPY requirements.txt .
# RUN pip install -r requirements.txt

RUN pip install --no-cache-dir \
    aiohttp \
    redis \
    prometheus_client \
    rich \
    python-dotenv \
    beautifulsoup4 \
    requests \
    schedule \
    openai

# Copy the rest of the application
COPY . .

# Default command (overridden by docker-compose)
CMD ["python3", "empire_orchestrator.py"]
