# AI Chat CLI

A simple command-line interface for chatting with OpenAI's GPT models.

## Features

- Interactive chat interface with conversation history
- Streaming responses for real-time interaction
- Conversation history management (keeps last 10 messages)
- Easy access via shell alias

## Setup

1. Clone the repository:
```bash
git clone https://github.com/syounglee012/ai-chat-cli.git
cd ai-chat-cli
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Add an alias to your `.zshrc` or `.bashrc`:
```bash
alias chat='/path/to/ai-chat-cli/chat.sh'
```

## Usage

Run the chat interface:
```bash
./chat.sh
```

Or if you've set up the alias:
```bash
chat
```

Type your messages and press Enter. Type `q` to quit.

## Requirements

- Python 3.9+
- OpenAI API key

## Dependencies

- `openai>=2.8.0` - OpenAI Python client
- `python-dotenv>=1.2.0` - Environment variable management
- `prompt-toolkit>=3.0.0` - Enhanced terminal interface

