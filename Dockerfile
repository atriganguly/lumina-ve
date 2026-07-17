FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and psutil headers
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the rembg u2net model to cache so the first request doesn't stall
RUN python -c "import urllib.request; import os; os.makedirs('/root/.u2net', exist_ok=True); urllib.request.urlretrieve('https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx', '/root/.u2net/u2net.onnx')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]