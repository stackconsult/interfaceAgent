"""
Test cases for the agent module.
"""
import pytest
from app.agents.base_agent import BaseAgent, ValidatorAgent, AnalyzerAgent
from app.agents.registry import agent_registry


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent can be initialized with config."""
        config = {"key": "value"}
        
        class TestAgent(BaseAgent):
            async def execute(self, data):
                return data
        
        agent = TestAgent(config=config)
        assert agent.config == config
        assert agent.status == "inactive"
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle(self):
        """Test agent lifecycle hooks."""
        class TestAgent(BaseAgent):
            async def execute(self, data):
                return data
        
        agent = TestAgent()
        
        await agent.on_start()
        assert agent.status == "active"
        
        await agent.on_stop()
        assert agent.status == "inactive"


class TestValidatorAgent:
    """Test cases for ValidatorAgent."""
    
    @pytest.mark.asyncio
    async def test_validation_success(self):
        """Test successful validation."""
        config = {
            "rules": [
                {"field": "name", "type": "required"},
                {"field": "age", "type": "type", "expected": "number"},
            ]
        }
        agent = ValidatorAgent(config=config)
        
        data = {"name": "John", "age": 30}
        result = await agent.execute(data)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_validation_failure(self):
        """Test validation failure."""
        config = {
            "rules": [
                {"field": "name", "type": "required"},
                {"field": "age", "type": "type", "expected": "number"},
            ]
        }
        agent = ValidatorAgent(config=config)
        
        data = {"age": "not a number"}  # Missing name, wrong age type
        result = await agent.execute(data)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0


class TestAnalyzerAgent:
    """Test cases for AnalyzerAgent."""
    
    @pytest.mark.asyncio
    async def test_data_analysis(self):
        """Test data analysis."""
        agent = AnalyzerAgent()
        
        data = {"field1": "value1", "field2": None, "field3": 123}
        result = await agent.execute(data)
        
        assert "analysis" in result
        assert "insights" in result["analysis"]
        assert result["data"] == data


class TestAgentRegistry:
    """Test cases for AgentRegistry."""
    
    def test_builtin_agents_registered(self):
        """Test that built-in agents are registered."""
        agents = agent_registry.list_agents()
        
        assert "validator" in agents
        assert "analyzer" in agents
        assert "enricher" in agents
        assert "transformer" in agents
    
    def test_create_agent(self):
        """Test creating an agent from registry."""
        agent = agent_registry.create_agent("validator", config={})
        
        assert agent is not None
        assert isinstance(agent, ValidatorAgent)
    
    def test_register_custom_agent(self):
        """Test registering a custom agent."""
        class CustomAgent(BaseAgent):
            async def execute(self, data):
                return {"custom": True, **data}
        
        agent_registry.register("custom", CustomAgent)
        
        agents = agent_registry.list_agents()
        assert "custom" in agents
        
        agent = agent_registry.create_agent("custom")
        assert agent is not None
        assert isinstance(agent, CustomAgent)
