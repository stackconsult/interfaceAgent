"""
Agent Registry for managing and loading agents.
"""
from typing import Dict, Type, Optional
from app.agents.base_agent import BaseAgent, ValidatorAgent, AnalyzerAgent, EnricherAgent, TransformerAgent


class AgentRegistry:
    """Registry for managing available agents."""
    
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._register_builtin_agents()
    
    def _register_builtin_agents(self):
        """Register built-in agents."""
        self.register("validator", ValidatorAgent)
        self.register("analyzer", AnalyzerAgent)
        self.register("enricher", EnricherAgent)
        self.register("transformer", TransformerAgent)
    
    def register(self, name: str, agent_class: Type[BaseAgent]):
        """
        Register an agent.
        
        Args:
            name: Unique name for the agent
            agent_class: Agent class to register
        """
        self._agents[name] = agent_class
    
    def get_agent_class(self, name: str) -> Optional[Type[BaseAgent]]:
        """
        Get an agent class by name.
        
        Args:
            name: Name of the agent
            
        Returns:
            Agent class or None if not found
        """
        return self._agents.get(name)
    
    def create_agent(self, name: str, config: Dict = None) -> Optional[BaseAgent]:
        """
        Create an agent instance.
        
        Args:
            name: Name of the agent
            config: Configuration for the agent
            
        Returns:
            Agent instance or None if not found
        """
        agent_class = self.get_agent_class(name)
        if agent_class:
            return agent_class(config=config)
        return None
    
    def list_agents(self):
        """List all registered agents."""
        return list(self._agents.keys())


# Global agent registry
agent_registry = AgentRegistry()
