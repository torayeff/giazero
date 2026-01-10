import base64
import mimetypes
import subprocess
from pathlib import Path

from langchain.tools import tool


@tool
def list_directory(dir_path: str) -> str:
    """List all files and directories in the specified directory.

    Returns a newline-separated list of entries. Directories are marked with
    a trailing slash (e.g., "subdir/"). Entries are sorted alphabetically.

    Args:
        dir_path: Path to the directory to list (relative or absolute).

    Returns:
        Newline-separated list of files and directories, or an error message.
    """
    try:
        resolved_path = Path(dir_path).resolve()

        if not resolved_path.exists():
            return f"Error: Directory '{dir_path}' does not exist."

        if not resolved_path.is_dir():
            return f"Error: '{dir_path}' is not a directory."

        items = []
        for item in sorted(resolved_path.iterdir()):
            if item.is_dir():
                items.append(f"{item.name}/")
            else:
                items.append(item.name)

        if not items:
            return "Directory is empty."

        return "\n".join(items)

    except PermissionError:
        return f"Error: Permission denied to access '{dir_path}'."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def read_text_file(file_path: str) -> str:
    """Read and return the contents of a UTF-8 encoded text file.

    Suitable for source code, configuration files, markdown, JSON, and other
    text-based formats. Returns an error for binary or non-UTF-8 files.

    Args:
        file_path: Path to the text file (relative or absolute).

    Returns:
        The file contents as a string, or an error message.
    """
    try:
        resolved_path = Path(file_path).resolve()

        if not resolved_path.exists():
            return f"Error: File '{file_path}' does not exist."

        if not resolved_path.is_file():
            return f"Error: '{file_path}' is not a file."

        return resolved_path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return f"Error: '{file_path}' is not a valid text file. Use read_binary_file instead."
    except PermissionError:
        return f"Error: Permission denied to read '{file_path}'."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def read_binary_file(file_path: str) -> str:
    """Read a binary file and return its contents as a base64-encoded string.

    Handles any file type including executables, archives, and data files.
    The output can be decoded using standard base64 decoding.

    Args:
        file_path: Path to the binary file (relative or absolute).

    Returns:
        Base64-encoded file contents, or an error message.
    """
    try:
        resolved_path = Path(file_path).resolve()

        if not resolved_path.exists():
            return f"Error: File '{file_path}' does not exist."

        if not resolved_path.is_file():
            return f"Error: '{file_path}' is not a file."

        binary_data = resolved_path.read_bytes()
        return base64.b64encode(binary_data).decode("utf-8")

    except PermissionError:
        return f"Error: Permission denied to read '{file_path}'."
    except Exception as e:
        return f"Error reading binary file: {str(e)}"


@tool
def read_image_file(file_path: str) -> list:
    """Read an image file and return it in a format suitable for visual analysis.

    Use this tool to understand the image content and semantics.

    Supports PNG, JPG, JPEG, GIF, and WebP formats. Returns the image as a
    base64-encoded payload with MIME type metadata for multimodal processing.

    Args:
        file_path: Path to the image file (relative or absolute).

    Returns:
        List containing image metadata and base64 data, or an error message.
    """
    try:
        resolved_path = Path(file_path).resolve()

        if not resolved_path.exists():
            return [
                {"type": "text", "text": f"Error: File '{file_path}' does not exist."}
            ]

        if not resolved_path.is_file():
            return [{"type": "text", "text": f"Error: '{file_path}' is not a file."}]

        mime_type = mimetypes.guess_type(str(resolved_path))[0]
        if mime_type is None or not mime_type.startswith("image/"):
            return [
                {
                    "type": "text",
                    "text": f"Error: '{file_path}' does not appear to be an image file.",
                }
            ]

        image_data = base64.b64encode(resolved_path.read_bytes()).decode("utf-8")

        return [
            {"type": "text", "text": f"Image: {resolved_path.name}"},
            {
                "type": "image",
                "source_type": "base64",
                "data": image_data,
                "mime_type": mime_type,
            },
        ]

    except PermissionError:
        return [
            {"type": "text", "text": f"Error: Permission denied to read '{file_path}'."}
        ]
    except Exception as e:
        return [{"type": "text", "text": f"Error reading image file: {str(e)}"}]


@tool
def write_file(file_path: str, content: str) -> str:
    """Write text content to a file, creating it if it doesn't exist.

    Overwrites existing files. Automatically creates parent directories
    as needed. Content is written with UTF-8 encoding.

    Args:
        file_path: Destination path for the file (relative or absolute).
        content: Text content to write to the file.

    Returns:
        Success confirmation message, or an error message.
    """
    try:
        resolved_path = Path(file_path).resolve()

        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        resolved_path.write_text(content, encoding="utf-8")
        return f"Successfully written to '{file_path}'."

    except PermissionError:
        return f"Error: Permission denied to write to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def execute_shell(cmd: str) -> str:
    """Execute a shell command.

    Runs the command in a shell environment.
    Captures and returns both stdout and stderr streams.

    Args:
        cmd: Shell command string to execute.

    Returns:
        Combined stdout/stderr output with return code, or an error message.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            if output:
                output += "\n"
            output += f"STDERR:\n{result.stderr}"
        if result.returncode != 0:
            if output:
                output += "\n"
            output += f"Return code: {result.returncode}"

        return output if output else "Command executed successfully with no output."

    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def execute_python(file_path: str) -> str:
    """Execute a Python script.

    Runs the specified .py file using the Python interpreter.
    Captures and returns both stdout and stderr streams.

    Args:
        file_path: Path to the Python script (relative or absolute).

    Returns:
        Combined stdout/stderr output with return code, or an error message.
    """
    try:
        resolved_path = Path(file_path).resolve()

        if not resolved_path.exists():
            return f"Error: File '{file_path}' does not exist."

        if not resolved_path.is_file():
            return f"Error: '{file_path}' is not a file."

        if resolved_path.suffix != ".py":
            return f"Error: '{file_path}' is not a Python file."

        result = subprocess.run(
            ["python", str(resolved_path)],
            capture_output=True,
            text=True,
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            if output:
                output += "\n"
            output += f"STDERR:\n{result.stderr}"
        if result.returncode != 0:
            if output:
                output += "\n"
            output += f"Return code: {result.returncode}"

        return (
            output if output else "Python script executed successfully with no output."
        )

    except Exception as e:
        return f"Error executing Python file: {str(e)}"


tools = [
    list_directory,
    read_text_file,
    read_binary_file,
    read_image_file,
    write_file,
    execute_shell,
    execute_python,
]
