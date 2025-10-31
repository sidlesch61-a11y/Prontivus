# Disaster Recovery Plan

## Objectives
- RPO: ≤ 15 minutes
- RTO: ≤ 60 minutes

## Backups
- Database: nightly full + 15-min WAL/incrementals
- Object storage: encrypted (e.g., S3 with SSE-KMS), 30–90 day retention
- Config: backup compose files, Nginx conf, .env (encrypted vault)

### PostgreSQL
Using `pg_dump` for full and WAL archiving for point-in-time recovery (or managed provider PITR):

```bash
# Full backup
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h db -U postgres -d clinicore -F c -f /backups/clinicore_$(date +%F_%H%M).dump

# Verify
pg_restore -l /backups/clinicore_*.dump | head
```

Schedule via cron or CI job, upload to object storage.

## Restore Procedure
1. Declare incident, freeze writes
2. Provision new DB (or clean existing)
3. Restore latest good backup:
```bash
createdb -h db -U postgres clinicore || true
pg_restore -h db -U postgres -d clinicore --clean --if-exists /backups/clinicore_<stamp>.dump
```
4. Apply migrations:
```bash
docker compose -f docker-compose.prod.yml exec backend bash -lc "alembic upgrade head"
```
5. Bring up stack and verify health:
- `/api/health` 200
- Smoke tests (login, list patients, schedule appt)

## Blue/Green Rollback
- Keep previous version tagged; to rollback:
```bash
docker compose -f docker-compose.prod.yml pull backend frontend
# switch tags or set image to previous SHA
docker compose -f docker-compose.prod.yml up -d
```
- If using dual upstreams, repoint Nginx to previous service and reload

## Documentation & Drills
- Store runbooks in repo, review quarterly
- Perform restore drills at least twice a year and document findings

## Contacts
- On-call SRE: <name/email>
- Security: <name/email>
