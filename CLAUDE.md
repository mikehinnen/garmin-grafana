# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Garmin-Grafana is a Docker application that fetches health data from Garmin Connect and visualizes it in Grafana using InfluxDB. The data pipeline: Garmin Connect API → Python fetcher → InfluxDB → Grafana dashboards.

## Development Commands

```bash
# Install dependencies (uses uv package manager)
uv sync --locked

# Run the main fetcher locally
uv run src/garmin_grafana/garmin_fetch.py

# Run with Docker Compose
docker compose up -d

# Kubernetes testing with minikube
cd k8s && make test-minikube
```

## Architecture

### Core Components (`src/garmin_grafana/`)

- **garmin_fetch.py** (1,473 lines): Main entry point. Handles Garmin OAuth via `garth`, fetches metrics (HR, sleep, stress, activities, etc.), parses FIT files for GPS/pace data, writes to InfluxDB. Runs on configurable interval (default 5 min).

- **garmin_bulk_importer.py**: Imports from Garmin bulk export ZIP files. Creates FIT file index for lookups.

- **fit_activity_importer.py**: Standalone FIT file importer. Uses MD5 hash for activity ID. Supports `--dry-run`.

- **influxdb_exporter.py**: Exports InfluxDB measurements to CSV/ZIP for external analysis.

### Data Flow

```
Garmin Connect API
    ↓ (python-garminconnect, garth for OAuth)
garmin_fetch.py
    ↓ (fitparse for FIT files)
InfluxDB (v1.x or v3.x)
    ↓
Grafana (pre-configured dashboard in Grafana_Dashboard/)
```

### Key Environment Variables

Required: `INFLUXDB_HOST`, `INFLUXDB_PORT`, `INFLUXDB_DATABASE`, `INFLUXDB_USERNAME`, `INFLUXDB_PASSWORD`

Optional: `GARMINCONNECT_EMAIL`, `GARMINCONNECT_BASE64_PASSWORD`, `UPDATE_INTERVAL_SECONDS`, `FETCH_SELECTION`, `MANUAL_START_DATE`/`MANUAL_END_DATE` (for bulk historical imports), `INFLUXDB_VERSION` ("1" or "3")

### InfluxDB Measurements

ActivitySummary, ActivityGPS, DailyAverage, Sleep, SleepStages, HeartRate, Steps, Stress, BodyBattery, Breathing, HRV, Calories, FitnessAge, VO2Max, TrainingStatus, TrainingReadiness, LactateThreshold

## Code Patterns

- Garmin OAuth tokens cached in `~/.garminconnect/` (1-year lifetime)
- 5-second delay between bulk API requests for rate limiting
- Supports both InfluxDB 1.x (port 8086) and 3.x (port 8181)
- Multi-user support via `TAG_MEASUREMENTS_WITH_USER_EMAIL`
- Garmin cold-archives intraday data older than 6 months

## Deployment

- **Docker Compose**: Primary method via `easy-install.sh` or `compose-example.yml`
- **Kubernetes/Helm**: Charts in `k8s/` with multi-arch images (amd64, arm64)
- Docker images: `thisisarpanghosh/garmin-fetch-data` (Docker Hub) and `ghcr.io`

## CI/CD

- `version.release.yml`: Triggered on `v*` tags, builds multi-arch Docker images, pushes to Docker Hub and GHCR
- Multi-stage Dockerfile using `uv` for dependency management, runs as non-root `appuser`
