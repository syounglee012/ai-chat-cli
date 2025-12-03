import os
from dotenv import load_dotenv
from openai import OpenAI
from prompt_toolkit import PromptSession

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def simple_chat(history: list, message: str) -> str:
    history.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=history,
        stream=True
    )

    assistant_message = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            assistant_message += content
    print()
    
    if assistant_message:
        history.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message


def main():
    session = PromptSession()
    history = []
    max_history = 10

    while True:
        message = session.prompt("You: ").strip()

        if message.lower() == "q":
            break

        if not message:
            continue

        simple_chat(history,message)

        if len(history) > max_history:
            history = history[-max_history:]
   
if __name__ == "__main__":
    main()

