import os
import subprocess


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        absolute_working_directory = os.path.abspath(working_directory)
        absolute_file_path = os.path.abspath(
            os.path.join(working_directory, file_path)
        )

        if os.path.commonpath(
            [absolute_working_directory, absolute_file_path]
        ) != absolute_working_directory:
            return (
                f'Error: Cannot execute "{file_path}" '
                "as it is outside the permitted working directory"
            )

        if not os.path.isfile(absolute_file_path):
            return (
                f'Error: "{file_path}" '
                "does not exist or is not a regular file"
            )

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", absolute_file_path]

        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            cwd=absolute_working_directory,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = []

        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        if not result.stdout and not result.stderr:
            output.append("No output produced")
        else:
            if result.stdout:
                output.append(f"STDOUT:\n{result.stdout}")

            if result.stderr:
                output.append(f"STDERR:\n{result.stderr}")

        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"
