"""Tests for configuration loader."""

import pytest
from unittest.mock import patch, mock_open

import config


class TestConfig:
    """Test cases for config module."""

    def setup_method(self):
        """Reset config cache before each test."""
        config._config = None

    def test_get_available_models_default(self):
        """Test default available models."""
        with patch('os.path.exists', return_value=False):
            config._config = None
            models = config.get_available_models()
            assert "gpt-4o-mini" in models
            assert len(models) == 4

    def test_get_default_model(self):
        """Test default model."""
        with patch('os.path.exists', return_value=False):
            config._config = None
            assert config.get_default_model() == "gpt-4o-mini"

    def test_get_aws_region(self):
        """Test AWS region."""
        with patch('os.path.exists', return_value=False):
            config._config = None
            assert config.get_aws_region() == "us-west-2"

    def test_get_history_limit(self):
        """Test history limit."""
        with patch('os.path.exists', return_value=False):
            config._config = None
            assert config.get_history_limit() == 20

    def test_load_config_from_yaml(self):
        """Test loading config from YAML file."""
        yaml_content = """
models:
  available:
    - test-model
  default: test-model
aws:
  region: us-east-1
memory:
  history_limit: 10
"""
        config._config = None
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=yaml_content)):
                cfg = config.load_config()
                assert cfg['models']['default'] == 'test-model'
                assert cfg['aws']['region'] == 'us-east-1'
                assert cfg['memory']['history_limit'] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
