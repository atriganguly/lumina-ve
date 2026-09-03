<div align="center">

# Lumina VE

**Marketplace Image Validation & Performance Intelligence Engine built for high-throughput scale.**

Created by [@atriganguly](https://github.com/atriganguly)

[Repository](https://github.com/atriganguly/lumina-ve) | [Live Demo](https://lumina-ve.onrender.com/demo) | [Documentation](https://lumina-ve.onrender.com/docs)

</div>

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0--beta-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)
![Language](https://img.shields.io/badge/Language-Python-informational)

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Problem Statement & Solution](#problem-statement--solution)
3. [Target Audience & Use Cases](#target-audience--use-cases)
4. [System Architecture](#system-architecture)
5. [Core Engineering Mechanics](#core-engineering-mechanics)
6. [Technology Stack](#technology-stack)
7. [Environment Configuration](#environment-configuration)
8. [Installation & Quick Start](#installation--quick-start)
9. [Operational Execution Modes](#operational-execution-modes)
10. [Data Lifecycle & Output Schema](#data-lifecycle--output-schema)
11. [Deployment & Infrastructure](#deployment--infrastructure)
12. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)
13. [AI Agent Execution Boundaries](#ai-agent-execution-boundaries)
14. [Support & Contributions](#support--contributions)
15. [License](#license)

## Executive Summary
Lumina VE is a high-performance, asynchronous REST microservice built to perform real-time multi-layered deep inspection on digital image assets. The system maintains operational visibility through structured JSON telemetry, offering a low-maintenance, memory-aware infrastructure that scales efficiently while reducing out-of-memory (OOM) crashes and operational overhead.

## Problem Statement & Solution

### The Problem
In modern e-commerce, subpar assets degrade customer trust and violate platform standards. 
* **System Volatility:** Machine learning frameworks like ONNX and `rembg` consume massive amounts of RAM, frequently causing container OOM crashes during heavy load.
* **High Infrastructure Overhead:** Synchronous CPU-intensive matrix computations starve event loops in standard web applications, crippling concurrency.
* **Security Vulnerabilities:** Processing unverified third-party image URLs creates severe Server-Side Request Forgery (SSRF) and Time-of-Check to Time-of-Use (TOCTOU) DNS rebinding risks.

### The Solution
Lumina VE resolves structural instability by introducing non-blocking thread-pool offloading and lazy-loaded neural runtimes.
* **Deterministic Execution:** Resolves hostnames to IP addresses asynchronously and overrides TLS SNI headers to strictly prevent SSRF attacks.
* **Cost & Overhead Reduction:** Analyzes system cgroups (v1/v2) and dynamically downgrades to lightweight non-ML algorithms (like OpenCV Canny edge-detection) if container memory dips below critical thresholds.
* **Audit-Ready Logging:** Explicitly warns users via a structured `system_warnings` array in the JSON response payload whenever fallback mechanics are triggered.

## Target Audience & Use Cases
* **Technical Leadership:** Provides clear visibility into image performance metrics, compliance standards, and CDN health.
* **Software & QA Engineers:** Delivers a resilient microservice architecture that avoids 500 server errors by safely degrading features under memory pressure.
* **Data & System Operations:** Guarantees deterministic image telemetry fetching (using strict `httpx` timeouts and file size limits).

## System Architecture
The application uses a decoupled architecture to isolate presentation, orchestration, execution, and persistent storage layers.

+-------------------+      +-------------------+      +-------------------+
|  FastAPI Router   | ---> |  Async Orchestrator| ---> |  Worker Threads   |
|  (Client Layer)   |      |  (HTTPX / Core)    |      |  (OpenCV / ONNX)  |
+-------------------+      +-------------------+      +-------------------+
                                     |                          |
                                     v                          v
                           +-------------------+      +-------------------+
                           |  Network Engine   |      | Output Artifacts  |
                           |  (SSRF / SNI Safe)|      |  (JSON Payload)   |
                           +-------------------+      +-------------------+

## Core Engineering Mechanics

### 1. Stateful Continuation & Relay
If fetching a URL exceeds the predefined `FETCH_TIMEOUT_SECONDS`, or the streaming data exceeds `MAX_FILE_SIZE_BYTES`, the network engine forcefully halts and gracefully returns a clear HTTP exception without crashing the container.

### 2. Deterministic State Locking
Execution paths are locked using an SSRF IP protection module. It uses `asyncio.getaddrinfo` to resolve the target domain's IP. The network driver then actively checks this IP against private, loopback, and link-local CIDR boundaries before initializing the stream.

### 3. Memory-Bounded Batch Processing
Prior to deep learning execution, Lumina VE reads `/sys/fs/cgroup/memory.max` (cgroups v2) or `memory.limit_in_bytes` (cgroups v1). If free RAM sits below `MIN_RAM_REQUIRED_MB`, `rembg` loading is skipped to save ~60MB-90MB, triggering the Canny fallback.

### 4. Graceful Error & Failure Isolation
When dependencies fail or connections break, operations throw explicit warnings nested inside `system_warnings` while retaining a `PARTIAL_SUCCESS` status label for whatever computations succeeded.

## Technology Stack

| Category | Technology | Operational Purpose |
| :--- | :--- | :--- |
| **Core Engine** | Python 3.10 | Primary runtime environment and business logic execution. |
| **API Framework** | FastAPI & Uvicorn | Asynchronous request handling, OpenAPI documentation, and endpoints. |
| **Computer Vision**| OpenCV & rembg | Background segmentation, Laplacian blur variance, and K-Means color clustering. |
| **Network & I/O** | HTTPX & Pillow | DNS rebinding protection via strict IP streaming, metadata property extraction. |

## Environment Configuration
System settings are managed independently of application logic through a `.env` file.

### Configuration Parameters Matrix
| Variable Name | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | String | `dev` | Toggles SSRF IP blocking checks (`dev` vs `production`). |
| `LUMINA_API_KEY` | String | *Required* | API Authentication Key for X-API-Key header. |
| `ENABLE_HEAVY_ML` | Boolean | `true` | Toggles ONNX Deep Learning K-Means & Segmentation. |
| `MIN_RAM_REQUIRED_MB` | Integer | `400` | Free megabytes required to trigger `rembg` ML load. |
| `FETCH_TIMEOUT_SECONDS` | Integer | `15` | Maximum wait duration in seconds before HTTP abort. |
| `MAX_FILE_SIZE_BYTES` | Integer | `26214400` | Stream abort threshold in bytes (Default: 25MB). |

## Installation & Quick Start

### Prerequisites
* Python 3.10+ installed and configured in your system environment.

### Step-by-Step Setup
1. **Clone the Repository**
   ```bash
   git clone [https://github.com/atriganguly/lumina-ve.git](https://github.com/atriganguly/lumina-ve.git)
   cd lumina-ve
   ```
2. **Configure Environment Parameters**
   ```bash
   cp .env.sample .env
   ```
   Open `.env` and fill in the required `LUMINA_API_KEY`.
3. **Initialize the Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Launch the Core Engine**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

## Operational Execution Modes
The engine can be initialized under distinct operational profiles depending on performance and resource requirements:
* **Heavy ML Mode (`ENABLE_HEAVY_ML=true`):** Performs U2-Net deep learning model background segmentation and precision K-Means RGB cluster extractions.
* **Lite / Fallback Mode (`ENABLE_HEAVY_ML=false`):** Skips all neural frameworks and downgrades to OpenCV Canny edge-dilation and simple color quantization binning, saving severe CPU/Memory strain.

## Data Lifecycle & Output Schema
Upon POST to `/v1/vision/validate/url`, the system returns the following schema:

### Primary Output Schema (`ValidationResponse`)
| Field Name | Data Type | Field Description |
| :--- | :--- | :--- |
| `url` | String | Original string submitted for inspection. |
| `status` | String | System result (`VALIDATION_PASSED` or `PARTIAL_SUCCESS`). |
| `system_warnings` | Array | Optional error/degradation context tracking ML failure hooks. |
| `network_intelligence` | JSON Object | `status_code`, `is_alive`, `dns_resolution_ip`, `ttfb_ms`, `download_duration_ms`, and `geo_location`. |
| `asset_properties` | JSON Object | `file_size_bytes`, `format`, `dimensions`, `color_space`, and `compression_ratio`. |
| `marketplace_compliance`| JSON Object | `is_blurry`, `blur_variance_score`, `is_amazon_compliant`, `pure_white_background_percentage`, `foreground_to_background_ratio`, and `bounding_box_padding_pct`. |
| `content_intelligence` | JSON Object | A `perceptual_hash` string and a `dominant_colors` array containing `hex_code` strings and `percentage` floats. |

## Deployment & Infrastructure

### Render YAML Config
Deploy natively to Render using the pre-configured `render.yaml` configuration:
* Assigns container to `oregon` region under `starter` plan.
* Health checks automatically routed to `/health` endpoint.

### Docker Containerization
Deploy the application inside an isolated Linux container:
```bash
docker build -t lumina-ve:latest .
docker run -d -p 8000:8000 --env-file .env lumina-ve:latest
```
*Note: The underlying Dockerfile automatically fetches and mounts the U2-Net `.onnx` models into the `/app/.u2net` directory so the image size remains stable.*

## Troubleshooting & Diagnostics
* **Issue: Server crashes abruptly when evaluating large product catalogs.**
  * *Cause:* Host environment memory limit reached by ONNX.
  * *Resolution:* Ensure your system cgroups v1/v2 metrics are mounted correctly for the container. Increase `MIN_RAM_REQUIRED_MB` to force earlier regression to Lite Mode.
* **Issue: `400 Bad Request` regarding forbidden internal IPs.**
  * *Cause:* SSRF protections blocking a target.
  * *Resolution:* In local testing, ensure your `.env` specifies `ENVIRONMENT=dev` to bypass IP-blocklist constraints.
* **Issue: CDN keeps returning 421 or 403.**
  * *Cause:* Typical Python web-scraping blocks or SNI mismatches.
  * *Resolution:* Lumina VE's network core injects the original `Host` and TLS `sni_hostname` artificially; if blocked, check the strict HTTPX timeout limits.

## AI Agent Execution Boundaries
Autonomous LLMs, coding agents, and automated patch routines operating on this codebase must adhere to these structural boundaries:
1. Maintain strict decoupling between configuration parameters and core execution engines.
2. Any CPU-intensive `cv2` or `rembg` additions MUST be wrapped in `asyncio.get_running_loop().run_in_executor()`.
3. Ensure strict file limitations remain inside `httpx` chunk streaming bounds to avoid infinite allocation attacks.
4. Consult `api/schemas.py` for response standards before injecting arbitrary `Dict` variables.

## Support & Contributions
This project is actively maintained to deliver reliable, open-source automation and execution infrastructure.
* **Bug Reports & Feature Suggestions:** [https://github.com/atriganguly/support/](https://github.com/atriganguly/support/)
* **Direct Enquiries:** Contact [@atriganguly](https://github.com/atriganguly) for technical questions, contributions, or pull request reviews.

## License
Distributed under the [GNU General Public License v3.0](LICENSE).