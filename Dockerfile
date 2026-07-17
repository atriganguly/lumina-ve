FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set U2NET_HOME explicitly so rembg always knows where to find the model, regardless of user
ENV U2NET_HOME=/app/.u2net
RUN python -c "import urllib.request; import os; os.makedirs('/app/.u2net', exist_ok=True); urllib.request.urlretrieve('https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx', '/app/.u2net/u2net.onnx')"

COPY . .

# Use the shell form of CMD so the $PORT environment variable injected by Render is correctly evaluated
# If $PORT is empty (like during local testing), it gracefully falls back to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}