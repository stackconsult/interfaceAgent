#!/usr/bin/env python3
"""
Setup script to initialize the application.
"""
import asyncio
import sys
from app.core.database import init_db, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import User, Role, Permission, Agent, AgentType, AgentStatus


async def create_superuser():
    """Create a default superuser."""
    async with AsyncSessionLocal() as db:
        # Check if superuser already exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Superuser already exists")
            return
        
        # Create superuser
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )
        
        db.add(admin)
        await db.commit()
        print("Superuser created: admin / admin123")


async def create_default_roles():
    """Create default roles."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        roles = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "developer", "description": "Developer with pipeline and agent access"},
            {"name": "analyst", "description": "Analyst with read-only access"},
            {"name": "operator", "description": "Operator with execution access"},
        ]
        
        for role_data in roles:
            result = await db.execute(select(Role).where(Role.name == role_data["name"]))
            if not result.scalar_one_or_none():
                role = Role(**role_data)
                db.add(role)
        
        await db.commit()
        print("Default roles created")


async def create_default_agents():
    """Create default agents."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        agents = [
            {
                "name": "Data Validator",
                "description": "Validates incoming data against configured rules",
                "agent_type": AgentType.VALIDATOR,
                "status": AgentStatus.ACTIVE,
                "config": {
                    "rules": [
                        {"field": "id", "type": "required"},
                        {"field": "timestamp", "type": "required"},
                    ]
                },
                "version": "1.0.0",
            },
            {
                "name": "Data Analyzer",
                "description": "Analyzes data patterns and extracts insights",
                "agent_type": AgentType.ANALYZER,
                "status": AgentStatus.ACTIVE,
                "config": {},
                "version": "1.0.0",
            },
            {
                "name": "Data Enricher",
                "description": "Enriches data with additional metadata",
                "agent_type": AgentType.ENRICHER,
                "status": AgentStatus.ACTIVE,
                "config": {},
                "version": "1.0.0",
            },
            {
                "name": "Data Transformer",
                "description": "Transforms data structure and format",
                "agent_type": AgentType.TRANSFORMER,
                "status": AgentStatus.ACTIVE,
                "config": {
                    "mappings": {
                        "old_field": "new_field"
                    }
                },
                "version": "1.0.0",
            },
        ]
        
        for agent_data in agents:
            result = await db.execute(select(Agent).where(Agent.name == agent_data["name"]))
            if not result.scalar_one_or_none():
                agent = Agent(**agent_data)
                db.add(agent)
        
        await db.commit()
        print("Default agents created")


async def main():
    """Main setup function."""
    print("Initializing database...")
    await init_db()
    print("Database initialized")
    
    print("\nCreating superuser...")
    await create_superuser()
    
    print("\nCreating default roles...")
    await create_default_roles()
    
    print("\nCreating default agents...")
    await create_default_agents()
    
    print("\n✅ Setup completed successfully!")
    print("\nYou can now login with:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  Please change the default password after first login!")


if __name__ == "__main__":
    asyncio.run(main())
