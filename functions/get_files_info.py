import os

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))
        if os.path.commonpath([abs_working_dir, target_dir]) != abs_working_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        metadata = []
        for dir in os.listdir(target_dir):
            filepath = os.path.join(target_dir, dir)
            is_dir = os.path.isdir(filepath)
            file_size = os.path.getsize(filepath)
            format = f"- {dir}: file_size={file_size} bytes, is_dir={is_dir}"
            metadata.append(format)
        return "\n".join(metadata)
    except Exception as e:
        return f"Error: {e}"
