# Deployment Guide

## Images
- Backend: `backend/Dockerfile` (multi-stage)
- Frontend: `frontend/Dockerfile`

## Local Development

```bash
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Postgres: localhost:5432
- Redis: localhost:6379

## Production Stack

```bash
export POSTGRES_PASSWORD="<secure>"
export GRAFANA_ADMIN_PASSWORD="<secure>"
docker compose -f docker-compose.prod.yml up -d
```

Services:
- Nginx (TLS 1.3): 80/443
- Backend (FastAPI): internal at `backend:8000`
- Frontend (Next.js): internal at `frontend:3000`
- Postgres, Redis
- Prometheus (9090), Grafana (3001)
- Elasticsearch (9200), Kibana (5601)

Copy certificates to `deploy/nginx/certs/` as `fullchain.pem` and `privkey.pem`.

## CI/CD (GitHub Actions)
- Backend workflow: tests (pytest), build/push image to GHCR
- Frontend workflow: tests (jest), build/push image to GHCR
- Security: CodeQL, Dependabot weekly

Update image registry/org if not using GHCR.

## Blue/Green Deployment
Two approaches:
1) Dual services
- Run `backend_blue` (current) and bring up `backend_green` with new tag
- Switch Nginx upstream to point to green, reload Nginx
- Drain and remove blue

2) Tag rolling
- Push new image tag and update `docker-compose.prod.yml` image
- `docker compose -f docker-compose.prod.yml up -d` brings up new containers with minimal downtime

## Database Migrations
- Run Alembic/SQL migrations before switching traffic:
```bash
docker compose -f docker-compose.prod.yml exec backend bash -lc "alembic upgrade head"
```

## Monitoring & Logging
- Prometheus scrapes backend `/metrics` (implement a metrics endpoint or exporter)
- Grafana connects to Prometheus at `prometheus:9090`
- ELK: apps log to stdout; ship with Filebeat/Logstash if needed

## Security Hardening
- TLS 1.3 in Nginx, security headers enabled
- App-level rate limiting present; extend Nginx with `limit_req` zones for DDoS mitigation
- DB at-rest encryption: use encrypted volumes or cloud-managed encryption (e.g., RDS with KMS). For field-level, consider `pgcrypto`
- Regular patching via Dependabot and image rebuilds (weekly)

## Backups & DR
See `docs/DISASTER_RECOVERY.md` for backup schedule and restore runbook.
