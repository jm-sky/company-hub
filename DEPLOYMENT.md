# Production Deployment Guide

## Architecture

The production deployment uses Docker Compose with the following services:

- **Backend API** (FastAPI + Gunicorn): Port 8000
- **Frontend** (Next.js): Port 3000
- **PostgreSQL**: Internal network only
- **Redis**: Internal network only

**Reverse Proxy**: Caddy handles SSL and routing on VPS:
- `api.company-hub.dev-made.it` → Backend (port 8000)
- `company-hub.dev-made.it` → Frontend (port 3000)

## Prerequisites

1. Docker and Docker Compose installed
2. Git repository cloned
3. `.env.prod` configured with production values
4. Caddy configured for domains

## Initial Setup

1. **Clone repository**:
```bash
git clone <repository-url>
cd company-hub
```

2. **Configure environment**:
```bash
cp .env.prod.example .env.prod
# Edit .env.prod with production values
```

3. **Build and start**:
```bash
./scripts/deploy-prod.sh
```

## Deployment Commands

### Deploy/Update
```bash
./scripts/deploy-prod.sh
```
Pulls latest code, rebuilds images, and restarts services.

### Check Status
```bash
./scripts/status.sh
```
Shows container status and health checks.

### View Logs
```bash
# All services
./scripts/logs.sh

# Specific service
./scripts/logs.sh app       # Backend
./scripts/logs.sh frontend  # Frontend
./scripts/logs.sh db        # Database
./scripts/logs.sh redis     # Redis
```

### Manual Docker Commands

```bash
# Build specific service
docker-compose -f docker-compose.prod.yml build app
docker-compose -f docker-compose.prod.yml build frontend

# Restart specific service
docker-compose -f docker-compose.prod.yml restart app
docker-compose -f docker-compose.prod.yml restart frontend

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View container stats
docker stats
```

## Database Operations

### Run Migrations
```bash
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
```

### Create Migration
```bash
docker-compose -f docker-compose.prod.yml exec app alembic revision --autogenerate -m "description"
```

### Database Backup
```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U companyhub companyhub > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Database Restore
```bash
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U companyhub companyhub
```

## Caddy Configuration

Example Caddyfile configuration:

```caddy
api.company-hub.dev-made.it {
    reverse_proxy localhost:8000
}

company-hub.dev-made.it {
    reverse_proxy localhost:3000
}
```

Reload Caddy:
```bash
sudo systemctl reload caddy
```

## Monitoring

### Health Checks
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000/api/health`

### Container Resources
```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

### Disk Usage
```bash
docker system df
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs app

# Check container status
docker-compose -f docker-compose.prod.yml ps
```

### Database connection issues
```bash
# Verify database is running
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Verify connection string in .env.prod
```

### Frontend build issues
```bash
# Rebuild frontend with no cache
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Check build logs
docker-compose -f docker-compose.prod.yml logs frontend
```

### Clean rebuild
```bash
# Stop and remove everything
docker-compose -f docker-compose.prod.yml down -v

# Rebuild from scratch
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Performance Tuning

### Backend Workers
Edit `docker-compose.prod.yml` to adjust Gunicorn workers:
```yaml
command: gunicorn app.main:app -w 8 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
Recommended: `workers = (2 * CPU_cores) + 1`

### Frontend Scaling
Scale frontend containers:
```bash
docker-compose -f docker-compose.prod.yml up -d --scale frontend=3
```

Note: Requires Caddy load balancing configuration.

## Security Checklist

- [ ] `.env.prod` has strong passwords
- [ ] Database not exposed to internet
- [ ] Redis not exposed to internet
- [ ] CORS_ORIGINS configured correctly
- [ ] SECRET_KEY is cryptographically secure
- [ ] OAuth credentials configured
- [ ] reCAPTCHA enabled and configured
- [ ] Caddy handles SSL/TLS termination
- [ ] Regular backups scheduled

## Maintenance

### Update Dependencies
```bash
# Backend
docker-compose -f docker-compose.prod.yml exec app pip list --outdated

# Frontend
cd frontend && pnpm outdated
```

### Clean Docker Resources
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes (CAUTION: may delete data)
docker volume prune

# Full system cleanup
docker system prune -a --volumes
```

## Rollback

If deployment fails:

```bash
# Revert to previous commit
git reset --hard HEAD~1

# Rebuild and restart
./scripts/deploy-prod.sh
```

Or restore from backup and redeploy known-good commit.
