# AI Chat CLI

A command-line interface for chatting with multiple LLM models via AWS Bedrock AgentCore.

## Features

- **Multiple LLM Models**: Switch between Claude, GPT-4o, and more
- **Persistent Memory**: Conversation history stored in AWS AgentCore Memory
- **Session-based**: Conversations persist across app restarts
- **AWS SSO Integration**: Automatic login handling

## Architecture

```
┌──────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  Python CLI  │────▶│  AWS AgentCore      │────▶│  RubyLLM Agent  │
│              │     │  Memory (Events)    │     │  (Claude/GPT)   │
└──────────────┘     └─────────────────────┘     └─────────────────┘
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/syounglee012/ai-chat-cli.git
cd ai-chat-cli
```

2. Create a virtual environment (Python 3.12+):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file with your AWS ARNs:
```bash
AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-west-2:YOUR_ACCOUNT:runtime/YOUR_AGENT
MEMORY_ARN=arn:aws:bedrock-agentcore:us-west-2:YOUR_ACCOUNT:memory/YOUR_MEMORY
```

4. (Optional) Add an alias to your shell:
```bash
alias chat='/path/to/ai-chat-cli/chat.sh'
```

## Usage

Run the chat interface:
```bash
./chat.sh
```

### Commands

| Command | Description |
|---------|-------------|
| `/m` or `/models` | Select a different model (1-4) |
| `q` | Quit |

### Available Models

1. `claude-sonnet-4`
2. `claude-3-5-haiku`
3. `gpt-4o`
4. `gpt-4o-mini` (default)

## Requirements

- Python 3.12+
- AWS CLI configured with SSO
- Access to AWS Bedrock AgentCore

## Dependencies

- `boto3>=1.35.0` - AWS SDK
- `python-dotenv>=1.2.0` - Environment variable management
- `prompt-toolkit>=3.0.0` - Enhanced terminal interface
