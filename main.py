import os
import json
from call_function import available_functions
from prompts import system_prompt
from dotenv import load_dotenv
from openai import OpenAI
import argparse

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument( "user_prompt", type=str, help="User prompt")
    args = parser.parse_args()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise RuntimeError("environment variable wasn't found: api_key")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=0,
        tools=available_functions
    )

    if response.usage is None:
        raise RuntimeError("no usage")
    else:
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_args = json.loads(
                    tool_call.function.arguments or "{}"
                )
                print(
                    f"Calling function: "
                    f"{tool_call.function.name}({function_args})"
                )
        else:
            print(f"Response: {message.content}")












if __name__ == "__main__":
    main()
