# Developer Guide

## Getting Started

### Local Development Setup

#### Backend Development

1. **Set up Python environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your local configuration
```

3. **Start dependencies:**
```bash
# Option 1: Docker Compose (recommended)
docker-compose up -d postgres redis rabbitmq

# Option 2: Local installation
# Install PostgreSQL, Redis, and RabbitMQ manually
```

4. **Initialize database:**
```bash
# Run setup script
python setup.py

# Or manually create tables
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

5. **Run the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment:**
```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

3. **Start development server:**
```bash
npm start
```

## Project Structure

```
interface-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent framework
│   │   │   ├── base_agent.py
│   │   │   ├── registry.py
│   │   │   └── plugin_loader.py
│   │   ├── api/             # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── agents.py
│   │   │   └── pipelines.py
│   │   ├── core/            # Core functionality
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/          # Database models
│   │   │   ├── user.py
│   │   │   ├── agent.py
│   │   │   └── event.py
│   │   ├── services/        # Business logic
│   │   │   ├── audit.py
│   │   │   ├── event_bus.py
│   │   │   ├── pii_redaction.py
│   │   │   └── anomaly_detection.py
│   │   └── main.py          # FastAPI app
│   ├── tests/               # Tests
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API services
│   │   └── App.js
│   └── package.json
└── docs/                    # Documentation
```

## Creating Custom Agents

### Basic Agent

```python
from app.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    """My custom agent that processes data."""
    
    async def execute(self, data: dict) -> dict:
        """
        Main processing logic.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed data dictionary
        """
        # Your custom logic here
        result = {
            "processed": True,
            "original": data,
            "custom_field": "custom_value",
        }
        return result
    
    async def validate_input(self, data: dict) -> bool:
        """Validate input data before processing."""
        required_fields = ["id", "type"]
        return all(field in data for field in required_fields)
    
    async def on_error(self, error: Exception, data: dict):
        """Handle errors during processing."""
        print(f"Error processing data: {error}")
```

### Registering an Agent

```python
from app.agents.registry import agent_registry

# Register your agent
agent_registry.register("my_custom_agent", MyCustomAgent)

# Create an instance
agent = agent_registry.create_agent("my_custom_agent", config={
    "param1": "value1",
    "param2": "value2",
})

# Execute
result = await agent.execute({"id": 1, "type": "test"})
```

### Plugin Agent

Create a plugin file `plugins/my_plugin.py`:

```python
from app.agents.base_agent import BaseAgent

class MyPluginAgent(BaseAgent):
    """A plugin agent loaded dynamically."""
    
    async def execute(self, data: dict) -> dict:
        # Plugin logic
        return data
```

Load the plugin:

```python
from app.agents.plugin_loader import plugin_loader

agent = plugin_loader.load_plugin(
    "plugins.my_plugin",
    "my_plugin_agent",
    config={"setting": "value"}
)
```

## API Development

### Creating New Endpoints

1. **Create a new router file:**
```python
# app/api/my_resource.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/")
async def list_resources(current_user = Depends(get_current_user)):
    return {"resources": []}

@router.post("/")
async def create_resource(data: dict, current_user = Depends(get_current_user)):
    return {"created": True}
```

2. **Add router to main app:**
```python
# app/main.py
from app.api import my_resource

app.include_router(my_resource.router, prefix="/api/my-resource", tags=["My Resource"])
```

### Adding RBAC Protection

```python
from app.api.deps import RBACChecker

@router.post("/")
async def create_resource(
    data: dict,
    current_user = Depends(RBACChecker("resource", "create"))
):
    # Only users with create permission on resource can access
    return {"created": True}
```

## Database Development

### Creating Models

```python
from app.models.base import BaseModel
from sqlalchemy import Column, String, Integer

class MyModel(BaseModel):
    """My custom model."""
    __tablename__ = "my_model"
    
    name = Column(String(100), nullable=False)
    value = Column(Integer)
```

### Creating Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add my_model table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_agents.py

# With coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Writing Tests

```python
import pytest
from app.models import User

@pytest.mark.asyncio
async def test_user_creation(db_session):
    """Test creating a user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
```

## Frontend Development

### Creating Components

```javascript
// src/components/MyComponent.js
import React, { useState, useEffect } from 'react';
import { myAPI } from '../services/api';

const MyComponent = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await myAPI.list();
      setData(response.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
};

export default MyComponent;
```

### Adding API Services

```javascript
// src/services/api.js
export const myAPI = {
  list: () => api.get('/api/my-resource/'),
  get: (id) => api.get(`/api/my-resource/${id}`),
  create: (data) => api.post('/api/my-resource/', data),
  update: (id, data) => api.put(`/api/my-resource/${id}`, data),
  delete: (id) => api.delete(`/api/my-resource/${id}`),
};
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Document with docstrings
- Format with Black
- Sort imports with isort

```bash
# Format code
black app/
isort app/

# Check style
flake8 app/ --max-line-length=100
```

### JavaScript

- Use ES6+ features
- Follow React best practices
- Use functional components with hooks
- Name files with PascalCase for components

## Debugging

### Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use IDE debugger with uvicorn
# Launch configuration in VS Code:
{
    "name": "Python: FastAPI",
    "type": "python",
    "request": "launch",
    "module": "uvicorn",
    "args": [
        "app.main:app",
        "--reload"
    ]
}
```

### Frontend Debugging

- Use React DevTools browser extension
- Use browser console for debugging
- Add console.log statements
- Use debugger statement in code

## Common Tasks

### Add a New Database Table

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Generate migration: `alembic revision --autogenerate -m "Add table"`
4. Review and apply: `alembic upgrade head`

### Add Authentication to Endpoint

```python
from app.api.deps import get_current_user

@router.get("/protected")
async def protected_endpoint(current_user = Depends(get_current_user)):
    return {"user": current_user.username}
```

### Add RBAC Permission

```python
from app.api.deps import RBACChecker

@router.post("/admin-only")
async def admin_endpoint(current_user = Depends(RBACChecker("admin", "execute"))):
    return {"success": True}
```

### Enable a Feature Flag

```bash
# In .env
ENABLE_ML_ANOMALY=true
ENABLE_PII_REDACTION=true
```

## Troubleshooting

### Common Issues

**Database connection errors:**
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Verify database exists

**Import errors:**
- Check Python path
- Ensure all __init__.py files exist
- Verify package installation

**Frontend can't connect:**
- Check REACT_APP_API_URL
- Verify CORS settings in backend
- Check network/firewall

### Getting Help

- Check logs: `docker-compose logs -f`
- Review documentation: `docs/`
- Check issues on GitHub
- Ask in team chat

## Best Practices

1. **Write tests** for new features
2. **Use type hints** in Python code
3. **Document** complex logic
4. **Follow** existing patterns
5. **Review** code before committing
6. **Keep** dependencies updated
7. **Use** meaningful commit messages
8. **Handle** errors gracefully
9. **Log** important events
10. **Security** first - validate all inputs
