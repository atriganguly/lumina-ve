<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="[https://api.iconify.design/lucide:eye.svg?color=white](https://api.iconify.design/lucide:eye.svg?color=white)">
    <source media="(prefers-color-scheme: light)" srcset="[https://api.iconify.design/lucide:eye.svg?color=111827](https://api.iconify.design/lucide:eye.svg?color=111827)">
    <img src="[https://api.iconify.design/lucide:eye.svg?color=111827](https://api.iconify.design/lucide:eye.svg?color=111827)" width="40" height="40" alt="Lumina VE Icon"/>
  </picture>
  <h1>Lumina VE</h1>
  <p>Marketplace Image Validation & Performance Intelligence Engine built for high-throughput scale.</p>
  
  <p>
    Created by 
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="[https://api.iconify.design/fa6-brands/github.svg?color=white](https://api.iconify.design/fa6-brands/github.svg?color=white)">
      <source media="(prefers-color-scheme: light)" srcset="[https://api.iconify.design/fa6-brands/github.svg?color=111827](https://api.iconify.design/fa6-brands/github.svg?color=111827)">
      <img src="[https://api.iconify.design/fa6-brands/github.svg?color=111827](https://api.iconify.design/fa6-brands/github.svg?color=111827)" width="16" height="16" style="vertical-align: middle; margin-bottom: 2px;" alt="GitHub"/>
    </picture>
    <a href="[https://github.com/atriganguly](https://github.com/atriganguly)"><b>@atriganguly</b></a> &nbsp;&bull;&nbsp; 
    <a href="[https://github.com/atriganguly/lumina-ve](https://github.com/atriganguly/lumina-ve)"><b>View Repository</b></a> &nbsp;&bull;&nbsp; 
    <a href="[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)"><b>Interactive API Docs</b></a>
  </p>
</div>

<br>

## Overview

In modern e-commerce and digital marketplaces, product image quality directly impacts conversion rates, search visibility, and platform compliance. Subpar assets—whether blurry, poorly framed, or hosted on slow CDN infrastructure—degrade customer trust and violate strict marketplace standards such as Amazon's product image requirements.

Lumina VE is a high-performance, asynchronous REST engine engineered to audit digital image assets in real time. It performs deep, multi-layered inspection across three core domains: **Network Intelligence** (latency, TTFB, GeoIP, streaming limits), **Asset Properties** (compression ratios, color spaces, metadata), and **Computer Vision Compliance** (Laplacian blur detection, background purity analysis, padding metrics, and perceptual hashing).

Built with resilience at its core, Lumina VE automatically scales its feature set based on container memory limits and environment toggles. It delivers sub-second insights on micro-tier instances while providing deep machine-learning analysis when hardware permits.

<br>

## Technology Stack

* **[FastAPI](https://fastapi.tiangolo.com/):** High-performance, asynchronous Python web framework providing OpenAPI specifications and fast request routing.
* **[OpenCV](https://opencv.org/):** Core computer vision engine used for Laplacian variance blur evaluation, spatial dimension calculations, and K-Means color matrix clustering.
* **[rembg & ONNX Runtime](https://github.com/danielgatis/rembg):** Machine learning pipeline utilizing the U2-Net deep learning model for foreground segmentation and background isolation.
* **[Pillow (PIL)](https://python-pillow.org/):** Image metadata processing library for format validation, channel inspection, and raw-to-compressed memory ratio calculations.
* **[HTTPX](https://www.python-httpx.org/):** Fully asynchronous HTTP client supporting stream-based downloads, strict timeout management, and network telemetry capture.
* **[ImageHash](https://github.com/JohannesBuchner/imagehash):** Perceptual hashing library used to compute 64-bit visual pHashes for image deduplication and similarity tracking.

<br>

## Getting Started

### 1. Environment Setup
Ensure Python 3.10 or higher is installed on your local machine.

```bash
# Clone the repository
git clone https://github.com/atriganguly/lumina-ve.git
cd lumina-ve

# Initialize virtual environment
python -m venv venv

# Activate virtual environment
# MacOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Lumina VE manages configuration via a root `.env` file. Create a `.env` file in your root project directory:

```env
ENVIRONMENT=dev
LUMINA_API_KEY=dev_lumina_secure_key_2026
ENABLE_HEAVY_ML=true
MIN_RAM_REQUIRED_MB=400
FETCH_TIMEOUT_SECONDS=15
MAX_FILE_SIZE_BYTES=26214400
```

### 3. Usage & Local Development
Start the application server using Uvicorn:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Once running, access the interactive OpenAPI documentation at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`. 

To validate an image via cURL, pass your API key in the `X-API-Key` request header:

```bash
curl -X POST http://127.0.0.1:8000/v1/vision/validate/url \
  -H "X-API-Key: dev_lumina_secure_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/images/hopper.png"
  }'
```

<br>

## Architecture & System Design
*A brief technical overview of the system's underlying engineering principles.*

Lumina VE was built to balance CPU-heavy computer vision tasks with high-concurrency web serving, avoiding event-loop starvation while offering rock-solid security and resource containment.

* **Non-Blocking Async Thread-Pool Offloading:** Synchronous CPU-intensive operations (such as OpenCV matrix transformations, K-Means clustering, and ONNX tensor evaluation) are wrapped inside Python's default thread executor via `asyncio.get_running_loop().run_in_executor()`. This guarantees that the FastAPI async event loop remains responsive to incoming HTTP traffic even under heavy analytical workloads.
* **SSRF Protection & TOCTOU DNS Rebinding Defense:** To prevent Server-Side Request Forgery (SSRF) and Time-of-Check to Time-of-Use (TOCTOU) DNS rebinding attacks, the dependency injection layer resolves the hostname to an IP address asynchronously and checks it against private, loopback, and link-local CIDR blocks. The subsequent transport step streams directly from the validated IP while retaining the original Host header.
* **Lazy-Loaded Neural Runtimes:** Machine learning frameworks like ONNX and `rembg` consume significant RAM upon import. Lumina VE defers the importing of `rembg` until runtime execution. If heavy ML operations are disabled or RAM is constrained, the dependencies are never loaded into memory, preserving a lightweight baseline footprint (~60MB–90MB).
* **Container-Aware Memory Safeguards (cgroups v1/v2):** Before initiating background segmentation, the engine queries operating system cgroups memory drivers (`/sys/fs/cgroup/memory.max` and `memory.limit_in_bytes`). If available RAM drops below `MIN_RAM_REQUIRED_MB` (e.g., 400MB), the engine dynamically bypasses the heavy ML steps to prevent container Out-Of-Memory (OOM) crashes.
* **Explicit System Warning Lifecycle:** Rather than failing silently or raising generic 500 errors when features are disabled or degraded, Lumina VE captures operational warnings into a structured `system_warnings` array and returns a `PARTIAL_SUCCESS` payload status to give API consumers transparent insight into skipped operations.

<br>

## Support & Contributions

I built Lumina VE to provide developer teams with a fast, memory-safe tool for marketplace image compliance and web asset verification.

If you discover a bug, want to discuss architectural enhancements, or need support patching edge cases, please feel free to contribute.

* **Bug Reports & Feature Requests:** [Open an Issue](https://github.com/atriganguly/lumina-ve/issues)
* **Connect:** Reach out via my [GitHub Profile](https://github.com/atriganguly) for patches, suggestions, or technical discussions.