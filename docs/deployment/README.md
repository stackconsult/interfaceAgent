# Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for K8s deployment)
- 4GB RAM minimum
- 20GB disk space

## Environment Configuration

### Backend Environment Variables

Create `backend/.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/interface_agent
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Security
SECRET_KEY=your-very-secure-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Features
ENABLE_ML_ANOMALY=true
ENABLE_PII_REDACTION=true
ENABLE_PLUGIN_SYSTEM=true
ENABLE_AUDIT_LOG=true

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Monitoring
PROMETHEUS_PORT=9090
ENABLE_METRICS=true
```

## Docker Deployment

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale workers
docker-compose up -d --scale celery_worker=3
```

## Kubernetes Deployment

### Prerequisites

1. Install kubectl
2. Configure cluster access
3. Create namespace:

```bash
kubectl create namespace interface-agent
```

### Deploy Services

```bash
# Apply configurations
kubectl apply -f infrastructure/kubernetes/postgres.yml
kubectl apply -f infrastructure/kubernetes/redis.yml
kubectl apply -f infrastructure/kubernetes/rabbitmq.yml
kubectl apply -f infrastructure/kubernetes/backend.yml
kubectl apply -f infrastructure/kubernetes/frontend.yml
kubectl apply -f infrastructure/kubernetes/ingress.yml

# Check status
kubectl get pods -n interface-agent
kubectl get services -n interface-agent
```

### Configure Ingress

Edit `infrastructure/kubernetes/ingress.yml`:

```yaml
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

## Database Migrations

### Initial Setup

```bash
# Inside backend container
docker-compose exec backend alembic upgrade head
```

### Create Migration

```bash
# After model changes
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migration
docker-compose exec backend alembic upgrade head
```

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d your-domain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

## Backup and Restore

### PostgreSQL Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U user interface_agent > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U user interface_agent < backup_20240101.sql
```

### Redis Backup

```bash
# Backup
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb

# Restore
docker cp redis_backup_20240101.rdb $(docker-compose ps -q redis):/data/dump.rdb
docker-compose restart redis
```

## Monitoring Setup

### Prometheus

1. Configure prometheus.yml
2. Add targets for backend metrics
3. Start Prometheus container

### Grafana

```bash
# Add Grafana to docker-compose.yml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
```

## Health Checks

Verify deployment:

```bash
# Backend health
curl http://localhost:8000/health

# Backend readiness
curl http://localhost:8000/ready

# Frontend
curl http://localhost:3000

# RabbitMQ
curl http://localhost:15672

# Metrics
curl http://localhost:8000/metrics
```

## Troubleshooting

### Backend won't start

1. Check logs: `docker-compose logs backend`
2. Verify environment variables
3. Check database connection
4. Ensure migrations are applied

### Database connection errors

1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check connection string in .env
3. Test connection: `docker-compose exec backend python -c "from app.core.database import engine; print('OK')"`

### Frontend can't connect to backend

1. Check REACT_APP_API_URL in frontend
2. Verify CORS settings in backend
3. Check network connectivity

### Performance Issues

1. Scale workers: `docker-compose up -d --scale celery_worker=5`
2. Increase database pool size
3. Add Redis memory
4. Enable caching

## Scaling

### Horizontal Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5

# Scale workers
kubectl scale deployment celery-worker --replicas=10
```

### Vertical Scaling

Update resource limits in Kubernetes:

```yaml
resources:
  limits:
    cpu: "2"
    memory: "4Gi"
  requests:
    cpu: "1"
    memory: "2Gi"
```

## Security Checklist

- [ ] Change default passwords
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS
- [ ] Set up rate limiting
- [ ] Configure backup retention
- [ ] Enable audit logging
- [ ] Review RBAC permissions
- [ ] Scan for vulnerabilities
- [ ] Update dependencies regularly
- [ ] Monitor security alerts

## Maintenance

### Regular Tasks

- Weekly: Review logs for errors
- Weekly: Check disk space
- Monthly: Update dependencies
- Monthly: Review security patches
- Quarterly: Disaster recovery drill
- Yearly: SSL certificate renewal

### Updates

```bash
# Update images
docker-compose pull
docker-compose up -d

# Or rebuild
docker-compose build --no-cache
docker-compose up -d
```
