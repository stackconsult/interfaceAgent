"""
Base Agent class for modular agent system.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize agent with configuration.

        Args:
            config: Agent-specific configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self._status = "inactive"

    @abstractmethod
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.

        Args:
            data: Input data for the agent

        Returns:
            Processed data
        """
        pass

    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data before processing.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        return True

    async def on_start(self):
        """Hook called when agent starts."""
        self._status = "active"

    async def on_stop(self):
        """Hook called when agent stops."""
        self._status = "inactive"

    async def on_error(self, error: Exception, data: Dict[str, Any]):
        """
        Hook called when an error occurs.

        Args:
            error: The exception that occurred
            data: The data being processed when error occurred
        """
        pass

    @property
    def status(self) -> str:
        """Get agent status."""
        return self._status

    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "config": self.config,
        }


class ValidatorAgent(BaseAgent):
    """Agent for validating data against schemas or rules."""

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against configured rules."""
        validation_rules = self.config.get("rules", [])
        errors = []

        for rule in validation_rules:
            field = rule.get("field")
            rule_type = rule.get("type")

            if field not in data:
                errors.append(f"Missing required field: {field}")
                continue

            value = data[field]

            if rule_type == "required" and not value:
                errors.append(f"Field {field} is required")
            elif rule_type == "type":
                expected_type = rule.get("expected")
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field {field} must be a string")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Field {field} must be a number")
            elif rule_type == "range":
                min_val = rule.get("min")
                max_val = rule.get("max")
                if isinstance(value, (int, float)):
                    if min_val is not None and value < min_val:
                        errors.append(f"Field {field} must be >= {min_val}")
                    if max_val is not None and value > max_val:
                        errors.append(f"Field {field} must be <= {max_val}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "data": data,
        }


class AnalyzerAgent(BaseAgent):
    """Agent for analyzing data and extracting insights."""

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and extract insights."""
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "data_size": len(str(data)),
            "fields_count": len(data.keys()) if isinstance(data, dict) else 0,
            "insights": [],
        }

        # Example analysis logic
        if isinstance(data, dict):
            # Check for missing values
            missing_fields = [k for k, v in data.items() if v is None or v == ""]
            if missing_fields:
                analysis["insights"].append(
                    {
                        "type": "missing_data",
                        "fields": missing_fields,
                    }
                )

            # Check for unusual data patterns
            numeric_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}
            if numeric_fields:
                analysis["insights"].append(
                    {
                        "type": "numeric_summary",
                        "fields": list(numeric_fields.keys()),
                        "count": len(numeric_fields),
                    }
                )

        return {
            "analysis": analysis,
            "data": data,
        }


class EnricherAgent(BaseAgent):
    """Agent for enriching data with additional information."""

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data with additional information."""
        enriched_data = data.copy()

        # Add metadata
        enriched_data["_enrichment"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "version": self.version,
        }

        # Apply custom enrichment rules from config
        enrichment_rules = self.config.get("rules", [])
        for rule in enrichment_rules:
            field = rule.get("add_field")
            value = rule.get("value")
            if field and value:
                enriched_data[field] = value

        return enriched_data


class TransformerAgent(BaseAgent):
    """Agent for transforming data structure or format."""

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to configured rules."""
        transformed_data = {}

        # Apply field mappings
        mappings = self.config.get("mappings", {})
        for source_field, target_field in mappings.items():
            if source_field in data:
                transformed_data[target_field] = data[source_field]

        # Copy unmapped fields if configured
        if self.config.get("copy_unmapped", False):
            for key, value in data.items():
                if key not in mappings and key not in transformed_data:
                    transformed_data[key] = value

        return transformed_data
