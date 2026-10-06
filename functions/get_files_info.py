from functions.paths import resolve_path
import os

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        target_dir = resolve_path(working_directory, directory)
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        metadata = []
        for dir in sorted(os.listdir(target_dir)):
            filepath = os.path.join(target_dir, dir)
            is_dir = os.path.isdir(filepath)
            file_size = os.path.getsize(filepath)
            format = f"- {dir}: file_size={file_size} bytes, is_dir={is_dir}"
            metadata.append(format)
        return "\n".join(metadata)
    except Exception as e:
        return f"Error: {e}"

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}
