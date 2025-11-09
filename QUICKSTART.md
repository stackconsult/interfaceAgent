# Quick Start Guide

Get the Interface Agent application up and running in under 5 minutes!

## Prerequisites

- Docker Desktop installed
- Git installed
- 4GB RAM available
- 10GB disk space

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/stackconsult/interfaceAgent.git
cd interfaceAgent
```

### 2. Configure Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Optional: Edit .env to customize settings
# nano backend/.env
```

### 3. Start the Application

```bash
# Start all services
docker-compose up -d

# Wait for services to start (about 30 seconds)
# Check status
docker-compose ps
```

### 4. Initialize the Database

```bash
# Run setup script to create admin user and default data
docker-compose exec backend python setup.py
```

You should see:
```
✅ Setup completed successfully!

You can now login with:
  Username: admin
  Password: admin123
```

### 5. Access the Application

Open your browser and navigate to:
- **Frontend:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **RabbitMQ Management:** http://localhost:15672 (guest/guest)

### 6. Login

1. Go to http://localhost:3000
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. **Important:** Change the password after first login!

## Quick Tour

### Dashboard

After logging in, you'll see the main dashboard with tiles for:
- **Agents** - Manage modular agents
- **Pipelines** - Create data processing pipelines
- **Monitoring** - View system metrics
- **Audit Logs** - Track all system actions
- **Plugins** - Manage custom plugins
- **Admin** - System administration

### Creating Your First Agent

1. Click on **Agents**
2. Click **Create Agent**
3. Fill in the details:
   - Name: "My First Agent"
   - Type: Validator
   - Description: "Validates incoming data"
4. Click **Create**
5. Click **Activate** to enable the agent

### Creating a Pipeline

1. Click on **Pipelines**
2. Click **Create Pipeline**
3. Name it "Data Processing Pipeline"
4. Add steps:
   - Step 1: Validator agent
   - Step 2: Analyzer agent
   - Step 3: Enricher agent
5. Activate the pipeline

### Testing the API

```bash
# Get access token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use the token for authenticated requests
TOKEN="your_token_here"

# List agents
curl http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN"

# Create an agent
curl -X POST http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Agent",
    "agent_type": "validator",
    "description": "Created via API"
  }'
```

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Application

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose build

# Restart
docker-compose up -d
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common fix: Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend python setup.py
```

### Frontend shows "Cannot connect"

1. Check if backend is running:
```bash
curl http://localhost:8000/health
```

2. Check CORS settings in `backend/.env`:
```
ALLOWED_ORIGINS=http://localhost:3000
```

### Database errors

```bash
# Reset database
docker-compose down
docker volume rm interfaceagent_postgres_data
docker-compose up -d
docker-compose exec backend python setup.py
```

### Port already in use

Change ports in `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8000 to 8001
  frontend:
    ports:
      - "3001:3000"  # Change 3000 to 3001
```

## Next Steps

### For Developers

1. Read the [Developer Guide](docs/developer-guide.md)
2. Review the [API Documentation](docs/api/README.md)
3. Check out example agents in `backend/app/agents/`
4. Write your first custom agent

### For Users

1. Explore the Dashboard
2. Create custom agents for your use case
3. Build pipelines for data processing
4. Review audit logs for compliance
5. Set up monitoring and alerts

### For Administrators

1. Review [Deployment Guide](docs/deployment/README.md)
2. Configure RBAC for your team
3. Set up backup schedules
4. Configure monitoring and metrics
5. Review security settings

## Resources

- **Documentation:** [docs/](docs/)
- **API Reference:** http://localhost:8000/docs
- **GitHub:** https://github.com/stackconsult/interfaceAgent
- **Issues:** https://github.com/stackconsult/interfaceAgent/issues

## Need Help?

- Check the [Troubleshooting Guide](docs/deployment/README.md#troubleshooting)
- Review [Common Issues](#troubleshooting)
- Open an issue on GitHub
- Contact support: support@interfaceagent.com

---

**Congratulations! 🎉** You've successfully set up Interface Agent!

Now explore the features and start building your data processing pipelines.
