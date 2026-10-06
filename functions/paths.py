"""Shared file-tool boundary checks (not a subprocess sandbox)."""
from pathlib import Path


def resolve_path(working_directory: str, relative_path: str) -> Path:
    root = Path(working_directory).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Working directory must be a directory")
    target = (root / relative_path).resolve()
    if not target.is_relative_to(root):
        raise ValueError("Path is outside the permitted working directory")
    return target
