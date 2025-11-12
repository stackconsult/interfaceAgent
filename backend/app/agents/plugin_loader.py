"""
Plugin system for loading custom agents.
"""

import importlib
from pathlib import Path
from typing import Any, Dict, Optional

from app.agents.base_agent import BaseAgent
from app.agents.registry import agent_registry
from app.core.config import get_settings

settings = get_settings()


class PluginLoader:
    """Loader for plugin agents."""

    def __init__(self):
        self.loaded_plugins: Dict[str, Any] = {}

    def load_plugin(
        self, module_path: str, plugin_name: str, config: Dict[str, Any] = None
    ) -> Optional[BaseAgent]:
        """
        Load a plugin agent from a module path.

        Args:
            module_path: Python module path (e.g., 'plugins.my_agent')
            plugin_name: Name to register the plugin under
            config: Configuration for the plugin

        Returns:
            Plugin agent instance or None if loading failed
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)

            # Look for a class that inherits from BaseAgent
            agent_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, type) and issubclass(item, BaseAgent) and item is not BaseAgent:
                    agent_class = item
                    break

            if not agent_class:
                raise ValueError(f"No agent class found in module {module_path}")

            # Register the agent
            agent_registry.register(plugin_name, agent_class)

            # Create instance
            agent = agent_class(config=config)
            self.loaded_plugins[plugin_name] = {
                "module_path": module_path,
                "class": agent_class,
                "instance": agent,
            }

            return agent

        except Exception as e:
            print(f"Error loading plugin {plugin_name} from {module_path}: {str(e)}")
            return None

    def unload_plugin(self, plugin_name: str):
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload
        """
        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]

    def list_loaded_plugins(self):
        """List all loaded plugins."""
        return list(self.loaded_plugins.keys())


# Global plugin loader
plugin_loader = PluginLoader()
