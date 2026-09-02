import os
import argparse

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function
from prompts import system_prompt


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "user_prompt",
        type=str,
        help="User prompt",
    )
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

    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            temperature=0,
            tools=available_functions,
        )

        if response.usage is None:
            raise RuntimeError("no usage")

        if args.verbose:
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message

        # Add the assistant's response to conversation history
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(
                    tool_call,
                    verbose=args.verbose,
                )

                if not result_message["content"]:
                    raise RuntimeError("tool call returned no content")

                # Add the tool result to conversation history
                messages.append(result_message)

                if args.verbose:
                    print(f"-> {result_message['content']}")
        else:
            print(f"Final response:\n{message.content}")
            break

    else:
        print("Maximum iterations reached without a final response.")


if __name__ == "__main__":
    main()
