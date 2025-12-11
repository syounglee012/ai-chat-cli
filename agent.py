"""AgentCore client for invoking agents and managing memory."""

import json
import uuid
from datetime import datetime, timezone
import boto3

# AgentCore clients
_client = None
_sts_client = None

def _get_client():
    global _client
    if _client is None:
        _client = boto3.client('bedrock-agentcore', region_name='us-west-2')
    return _client

def _get_sts_client():
    global _sts_client
    if _sts_client is None:
        _sts_client = boto3.client('sts', region_name='us-west-2')
    return _sts_client


class AgentClient:
    """Client for interacting with AWS Bedrock AgentCore."""
    
    def __init__(self, agent_arn: str, memory_arn: str = None):
        self.agent_arn = agent_arn
        self.memory_arn = memory_arn
    
    def _get_memory_id(self) -> str | None:
        """Extract memory ID from ARN."""
        if not self.memory_arn:
            return None
        return self.memory_arn.split('/')[-1]
    
    def get_session_id(self) -> str:
        """Get a unique session ID based on AWS user identity."""
        try:
            identity = _get_sts_client().get_caller_identity()
            user_id = identity['UserId']
            sanitized = user_id.replace(':', '_').replace('@', '_').replace('.', '_')
            base_id = f"session-{sanitized}"
            # Ensure at least 33 characters
            while len(base_id) < 33:
                base_id += "-0"
            return base_id
        except Exception:
            return str(uuid.uuid4()) + "-" + str(uuid.uuid4())[:8]
    
    
    def save_to_memory(self, session_id: str, role: str, content: str):
        """Save a message to AgentCore Memory."""
        if not self._get_memory_id():
            return
        
        actor_role = "USER" if role == "user" else "ASSISTANT"
        
        try:
            _get_client().create_event(
                memoryId=self._get_memory_id(),
                actorId=role,
                sessionId=session_id,
                eventTimestamp=datetime.now(timezone.utc),
                payload=[{
                    'conversational': {
                        'content': {'text': content},
                        'role': actor_role
                    }
                }],
                clientToken=str(uuid.uuid4()),
            )
        except Exception as e:
            print(f"Warning: Could not save to memory: {e}")
    
    def get_history(self, session_id: str) -> list:
        """Get conversation history from AgentCore Memory."""
        if not self._get_memory_id():
            return []
        
        try:
            history = []
            for actor in ["user", "assistant"]:
                try:
                    response = _get_client().list_events(
                        memoryId=self._get_memory_id(),
                        sessionId=session_id,
                        actorId=actor,
                        includePayloads=True,
                    )
                    for event in response.get('events', []):
                        for payload_item in event.get('payload', []):
                            conv = payload_item.get('conversational', {})
                            content = conv.get('content', {}).get('text', '')
                            role = conv.get('role', 'USER').lower()
                            timestamp = event.get('eventTimestamp')
                            if content:
                                history.append({
                                    "role": role,
                                    "content": content,
                                    "timestamp": timestamp
                                })
                except Exception:
                    pass
            
            history.sort(key=lambda x: x.get('timestamp', ''))
            return history
        except Exception as e:
            print(f"Warning: Could not get memory: {e}")
            return []
    
    def _build_prompt(self, history: list, message: str) -> str:
        """Build a prompt that includes conversation history."""
        if not history:
            return message
        
        conversation = ""
        for entry in history[-20:]:
            role = entry.get('role', 'unknown').lower()
            content = entry.get('content', '')
            if role == 'user':
                conversation += f"User: {content}\n"
            else:
                conversation += f"Assistant: {content}\n"
        
        conversation += f"User: {message}"
        return conversation
    
    def chat(self, message: str, session_id: str, model: str = None) -> str:
        """Send a message and get a streaming response."""
        history = self.get_history(session_id)
        full_prompt = self._build_prompt(history, message)
        
        payload = {"input": {"prompt": full_prompt}}
        if model:
            payload["input"]["model"] = model
        
        response = _get_client().invoke_agent_runtime(
            agentRuntimeArn=self.agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload),
            qualifier="DEFAULT"
        )
        
        print("\n-> ", end="", flush=True)
        
        response_body = response['response'].read().decode('utf-8')
        
        full_text = ""
        for line in response_body.split('\n'):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'event' in data and 'contentBlockDelta' in data['event']:
                        text = data['event']['contentBlockDelta']['delta'].get('text', '')
                        print(text, end="", flush=True)
                        full_text += text
                except json.JSONDecodeError:
                    pass
        
        print()
        
        # Save to memory
        self.save_to_memory(session_id, "user", message)
        self.save_to_memory(session_id, "assistant", full_text)
        
        return full_text
