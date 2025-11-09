# Interface Agent - Enterprise Agentic Enrichment Application

[![Backend CI/CD](https://github.com/stackconsult/interfaceAgent/workflows/Backend%20CI/CD/badge.svg)](https://github.com/stackconsult/interfaceAgent/actions)
[![Frontend CI/CD](https://github.com/stackconsult/interfaceAgent/workflows/Frontend%20CI/CD/badge.svg)](https://github.com/stackconsult/interfaceAgent/actions)

A production-ready enterprise agentic enrichment application with comprehensive features for data processing, validation, analysis, and enrichment using modular agents and pipelines.

## 🚀 Features

### Core Features
- **Modular Agent System**: Extensible agent framework with built-in validator, analyzer, enricher, and transformer agents
- **Pipeline Orchestration**: Configure multi-step data processing pipelines
- **Event Bus (HA)**: High-availability event processing with RabbitMQ and Redis
- **Admin API**: Comprehensive REST API for system management
- **Validator & Analyzer**: Built-in data validation and analysis capabilities
- **Audit Logging**: Complete audit trail of all system actions
- **RBAC**: Role-based access control with fine-grained permissions
- **PII Redaction**: Automated PII detection and redaction using Presidio
- **ML Anomaly Detection**: Machine learning-based anomaly detection
- **Escalation System**: Automated escalation for critical events
- **Plugin Registry**: Extensible plugin system for custom agents
- **Live Dashboard**: Real-time monitoring dashboard
- **Review Board**: Built-in review system for changes

### Security & Compliance
- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Security hardening best practices
- PII detection and redaction
- Comprehensive audit logging
- RBAC with fine-grained permissions

### DevOps & Production Readiness
- Docker & Docker Compose support
- Kubernetes-ready architecture
- CI/CD with GitHub Actions
- Health checks and readiness probes
- Prometheus metrics
- Disaster Recovery support
- Autoscaling configuration

## 📋 Architecture

### Technology Stack

**Backend:**
- Python 3.11
- FastAPI
- PostgreSQL (with SQLAlchemy async)
- Redis (caching & queue)
- RabbitMQ (event bus)
- Celery (background tasks)

**Frontend:**
- React 18
- Axios
- React Router
- WebSocket (for live updates)

**Infrastructure:**
- Docker & Docker Compose
- GitHub Actions
- Prometheus (metrics)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - Dashboard  - Agent Management  - Pipeline Builder        │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API / WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (Auth, Agents, Pipelines, Admin)         │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Services Layer                                      │   │
│  │  - Event Bus  - Audit Logger  - PII Redaction       │   │
│  │  - Anomaly Detection  - Plugin Loader                │   │
│  └──────────────────────┬───────────────────────────────┘   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │  Agent Framework                                     │   │
│  │  - Base Agent  - Validators  - Analyzers            │   │
│  │  - Enrichers  - Transformers  - Custom Plugins      │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌──────▼──────┐ ┌───────▼────────┐
│   PostgreSQL   │ │    Redis    │ │    RabbitMQ    │
│   (Database)   │ │   (Cache)   │ │  (Event Bus)   │
└────────────────┘ └─────────────┘ └────────────────┘
```

## 🔧 Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3+

### Quick Start with Docker

1. **Clone the repository:**
```bash
git clone https://github.com/stackconsult/interfaceAgent.git
cd interfaceAgent
```

2. **Configure environment:**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for PII detection
python -m spacy download en_core_web_sm

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📖 Usage

### Creating an Agent

```python
from app.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, data):
        # Your custom logic here
        result = process_data(data)
        return result
```

### Creating a Pipeline

```bash
# Using the API
curl -X POST http://localhost:8000/api/pipelines/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Processing Pipeline",
    "description": "Validates, analyzes, and enriches incoming data",
    "steps": [
      {"agent_id": 1, "order": 1},
      {"agent_id": 2, "order": 2},
      {"agent_id": 3, "order": 3}
    ]
  }'
```

### Using PII Redaction

```python
from app.services.pii_redaction import pii_service

text = "My email is john@example.com and phone is 555-1234"
redacted = pii_service.redact_pii(text)
# Output: "My email is *********** and phone is ********"
```

### Anomaly Detection

```python
from app.services.anomaly_detection import anomaly_service

data = {"user_id": 123, "action": "login", "count": 1000}
anomaly = await anomaly_service.detect_anomaly(db, data)
if anomaly:
    print(f"Anomaly detected: {anomaly['severity']}")
```

## 🔐 Security

### Authentication
- JWT tokens with configurable expiration
- Refresh token support
- Password hashing with bcrypt

### Authorization
- Role-based access control (RBAC)
- Fine-grained permissions per resource
- Superuser override capability

### Security Hardening
- SQL injection prevention (parameterized queries)
- XSS protection
- CORS configuration
- Rate limiting (TODO)
- Input validation
- Audit logging

## 📊 Monitoring

### Health Checks
- `/health` - Basic health check
- `/ready` - Readiness check
- `/metrics` - Prometheus metrics

### Metrics
- Request count and latency
- Agent execution metrics
- Pipeline performance
- Error rates
- Database connection pool stats

## 🚀 Deployment

### Docker Deployment

```bash
# Production build
docker-compose -f docker-compose.yml up -d

# Check logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale celery_worker=3
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f infrastructure/kubernetes/

# Check status
kubectl get pods
kubectl get services
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI framework
- React community
- All open-source contributors

## 📞 Support

For support, email support@interfaceagent.com or open an issue on GitHub.

---

**Interface Agent** - Production-ready enterprise agentic enrichment application 
