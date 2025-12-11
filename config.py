"""Configuration loader for AI Chat CLI."""

import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

_config = None


def load_config() -> dict:
    """Load configuration from YAML file."""
    global _config
    if _config is not None:
        return _config
    
    if not os.path.exists(CONFIG_PATH):
        # Return defaults if no config file
        _config = {
            "models": {
                "available": ["claude-sonnet-4", "claude-3-5-haiku", "gpt-4o", "gpt-4o-mini"],
                "default": "gpt-4o-mini"
            },
            "aws": {"region": "us-west-2"},
            "memory": {"history_limit": 20}
        }
        return _config
    
    with open(CONFIG_PATH, "r") as f:
        _config = yaml.safe_load(f)
    
    return _config


def get_available_models() -> list:
    """Get list of available models."""
    return load_config().get("models", {}).get("available", [])


def get_default_model() -> str:
    """Get default model name."""
    return load_config().get("models", {}).get("default", "gpt-4o-mini")


def get_aws_region() -> str:
    """Get AWS region."""
    return load_config().get("aws", {}).get("region", "us-west-2")


def get_history_limit() -> int:
    """Get number of history messages to include."""
    return load_config().get("memory", {}).get("history_limit", 20)
