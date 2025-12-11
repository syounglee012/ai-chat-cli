import os
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from agent import AgentClient

load_dotenv()

AGENT_RUNTIME_ARN = os.getenv("AGENT_RUNTIME_ARN")
MEMORY_ARN = os.getenv("MEMORY_ARN")

AVAILABLE_MODELS = [
    "claude-sonnet-4",
    "claude-3-5-haiku",
    "gpt-4o",
    "gpt-4o-mini",
]

DEFAULT_MODEL = "gpt-4o-mini"


def main():
    if not AGENT_RUNTIME_ARN:
        print("Error: AGENT_RUNTIME_ARN environment variable is not set.")
        return
    
    if not MEMORY_ARN:
        print("Warning: MEMORY_ARN not set. Conversation history will not persist.")

    # Initialize agent client
    agent = AgentClient(AGENT_RUNTIME_ARN, MEMORY_ARN)
    
    session = PromptSession()
    current_model = DEFAULT_MODEL
    session_id = agent.get_session_id()

    print("Commands:")
    print("  /models or /m  - List and select models (1-4)")
    print("  q              - Quit")

    try:
        while True:  
            prompt_text = f"\n[{current_model}] You: "
            message = session.prompt(prompt_text).strip()

            if message.lower() == "q":
                print("\nGoodbye!")
                break

            if not message:
                continue

            # Handle /models or /m command
            if message in ["/models", "/m"]:
                print("Available models:")
                for i, m in enumerate(AVAILABLE_MODELS, 1):
                    marker = " (current)" if m == current_model else ""
                    print(f"  {i}. {m}{marker}")
                print("\nEnter number to select: ", end="", flush=True)
                try:
                    choice = session.prompt("").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(AVAILABLE_MODELS):
                            current_model = AVAILABLE_MODELS[idx]
                            print(f"Model changed to {current_model}.")
                        else:
                            print("Invalid selection.")
                except (KeyboardInterrupt, EOFError):
                    pass
                continue

            agent.chat(message, session_id, current_model)
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except EOFError:
        print("\nGoodbye!")
   
if __name__ == "__main__":
    main()
