"""Tests for AgentClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from datetime import datetime, timezone

from agent import AgentClient


class TestAgentClient:
    """Test cases for AgentClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent_arn = "arn:aws:bedrock-agentcore:us-west-2:123456789:runtime/test-agent"
        self.memory_arn = "arn:aws:bedrock-agentcore:us-west-2:123456789:memory/test-memory"
        self.client = AgentClient(self.agent_arn, self.memory_arn)

    def test_init(self):
        """Test AgentClient initialization."""
        assert self.client.agent_arn == self.agent_arn
        assert self.client.memory_arn == self.memory_arn

    def test_get_memory_id(self):
        """Test memory ID extraction from ARN."""
        assert self.client._get_memory_id() == "test-memory"

    def test_get_memory_id_no_arn(self):
        """Test memory ID returns None when no ARN."""
        client = AgentClient(self.agent_arn, None)
        assert client._get_memory_id() is None

    @patch('agent._get_sts_client')
    def test_get_session_id(self, mock_sts):
        """Test session ID generation from AWS identity."""
        mock_sts.return_value.get_caller_identity.return_value = {
            'UserId': 'AROATEST:user@example.com'
        }
        
        session_id = self.client.get_session_id()
        
        assert session_id.startswith('session-AROATEST_user_example_com')
        assert len(session_id) >= 33

    @patch('agent._get_sts_client')
    def test_get_session_id_fallback(self, mock_sts):
        """Test session ID fallback when STS fails."""
        mock_sts.return_value.get_caller_identity.side_effect = Exception("STS error")
        
        session_id = self.client.get_session_id()
        
        # Should return UUID-based fallback
        assert len(session_id) >= 33

    def test_build_prompt_no_history(self):
        """Test prompt building with no history."""
        result = self.client._build_prompt([], "Hello")
        assert result == "Hello"

    def test_build_prompt_with_history(self):
        """Test prompt building with conversation history."""
        history = [
            {"role": "user", "content": "Hi", "timestamp": "2024-01-01T00:00:00Z"},
            {"role": "assistant", "content": "Hello!", "timestamp": "2024-01-01T00:00:01Z"},
        ]
        
        result = self.client._build_prompt(history, "How are you?")
        
        expected = "User: Hi\nAssistant: Hello!\nUser: How are you?"
        assert result == expected

    def test_build_prompt_limits_history(self):
        """Test that prompt limits history to last 20 messages."""
        history = [
            {"role": "user", "content": f"Message {i}", "timestamp": f"2024-01-01T00:00:{i:02d}Z"}
            for i in range(30)
        ]
        
        result = self.client._build_prompt(history, "New message")
        
        # Should only include last 20 messages
        assert "Message 10" in result
        assert "Message 29" in result
        assert "Message 9" not in result

    @patch('agent._get_client')
    def test_save_to_memory(self, mock_client):
        """Test saving message to memory."""
        self.client.save_to_memory("session-123", "user", "Hello")
        
        mock_client.return_value.create_event.assert_called_once()
        call_kwargs = mock_client.return_value.create_event.call_args[1]
        
        assert call_kwargs['memoryId'] == 'test-memory'
        assert call_kwargs['actorId'] == 'user'
        assert call_kwargs['sessionId'] == 'session-123'
        assert call_kwargs['payload'][0]['conversational']['content']['text'] == 'Hello'
        assert call_kwargs['payload'][0]['conversational']['role'] == 'USER'

    @patch('agent._get_client')
    def test_save_to_memory_assistant(self, mock_client):
        """Test saving assistant message to memory."""
        self.client.save_to_memory("session-123", "assistant", "Hi there!")
        
        call_kwargs = mock_client.return_value.create_event.call_args[1]
        assert call_kwargs['payload'][0]['conversational']['role'] == 'ASSISTANT'

    def test_save_to_memory_no_memory_arn(self):
        """Test save_to_memory does nothing without memory ARN."""
        client = AgentClient(self.agent_arn, None)
        # Should not raise
        client.save_to_memory("session-123", "user", "Hello")

    @patch('agent._get_client')
    def test_get_history(self, mock_client):
        """Test getting conversation history."""
        mock_client.return_value.list_events.return_value = {
            'events': [
                {
                    'eventTimestamp': '2024-01-01T00:00:00Z',
                    'payload': [{
                        'conversational': {
                            'content': {'text': 'Hello'},
                            'role': 'USER'
                        }
                    }]
                }
            ]
        }
        
        history = self.client.get_history("session-123")
        
        assert len(history) >= 1
        assert history[0]['content'] == 'Hello'
        assert history[0]['role'] == 'user'

    def test_get_history_no_memory_arn(self):
        """Test get_history returns empty list without memory ARN."""
        client = AgentClient(self.agent_arn, None)
        assert client.get_history("session-123") == []

    @patch('agent._get_client')
    def test_chat(self, mock_client):
        """Test chat method."""
        # Mock list_events to return empty history
        mock_client.return_value.list_events.return_value = {'events': []}
        
        # Mock invoke_agent_runtime response
        response_data = (
            'data: {"event":{"contentBlockDelta":{"delta":{"text":"Hello"}}}}\n'
            'data: {"event":{"contentBlockDelta":{"delta":{"text":" there!"}}}}\n'
        )
        mock_response = Mock()
        mock_response.read.return_value = response_data.encode('utf-8')
        mock_client.return_value.invoke_agent_runtime.return_value = {
            'response': mock_response
        }
        
        result = self.client.chat("Hi", "session-123", "gpt-4o-mini")
        
        assert result == "Hello there!"
        
        # Verify invoke was called with correct params
        call_kwargs = mock_client.return_value.invoke_agent_runtime.call_args[1]
        assert call_kwargs['agentRuntimeArn'] == self.agent_arn
        assert call_kwargs['runtimeSessionId'] == 'session-123'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
