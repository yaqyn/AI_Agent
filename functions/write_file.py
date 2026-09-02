import os


def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_path = os.path.normpath(
            os.path.join(abs_working_dir, file_path)
        )

        if os.path.commonpath([abs_working_dir, target_path]) != abs_working_dir:
            return (
                f'Error: Cannot write to "{file_path}" '
                "as it is outside the permitted working directory"
            )

        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        parent_dir = os.path.dirname(target_path)
        os.makedirs(parent_dir, exist_ok=True)

        with open(target_path, "w") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except OSError as e:
        return f"Error: {e}"







schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Writes or overwrites a file with the provided content",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write, relative to the working directory",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}
