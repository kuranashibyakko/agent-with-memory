import json
import os
from dotenv import load_dotenv
from groq import Groq
from tools import read, write

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-20b"

tools = [
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Saves a key-value fact or preference to persistent memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The category or topic (e.g., 'favorite_fruit').",
                    },
                    "description": {
                        "type": "string",
                        "description": "The specific detail or preference to remember (e.g., 'loves bananas').",
                    },
                },
                "required": ["subject", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Reads all stored facts and preferences from persistent memory.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

system_instruction = """
You are a helpful assistant with persistent memory.
1. Reading memory: Whenever the user asks about their preferences, personal details, or when answering could benefit from past personal context, use the read tool to inspect what is stored.
2. Writing memory: Whenever the user shares a fact, preference, or detail about themselves, use the write tool to save it with a clear subject and description.
Always give a natural, helpful response after using your tools.
"""

messages = [
    {"role": "system", "content": system_instruction},
]

print("Agent is ready! Type 'quit' or 'exit' to stop.")

while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() in ["quit", "exit"]:
        print("Goodbye!")
        break

    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    # Internal turn loop: handles tool calling and final answers cleanly
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        messages.append(message)

        # If the model produced a regular text reply, print it and wait for next user prompt
        if not message.tool_calls:
            print(f"\nAgent: {message.content}")
            break

        # Execute all tool calls returned by the model
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "write":
                result = write(
                    subject=arguments.get("subject", ""),
                    description=arguments.get("description", ""),
                )
            elif function_name == "read":
                result = read()
            else:
                result = "Function not found"

            print(f"DEBUG: Tool called '{function_name}' -> Returned: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })