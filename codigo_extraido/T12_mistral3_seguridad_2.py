import yaml
import os
from typing import Dict, Any
from pathlib import Path

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """
    Safely loads a YAML configuration file into a Python dictionary.

    Args:
        file_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the parsed YAML configuration.

    Raises:
        ValueError: If the file is empty, too large, or has invalid YAML.
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are insufficient permissions to read the file.
        yaml.YAMLError: If the YAML is malformed.
    """
    # Validate file path
    if not file_path:
        raise ValueError("File path cannot be empty")

    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check if it's a file (not a directory)
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Check file permissions (readable)
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Insufficient permissions to read file: {file_path}")

    # Check file size (limit to 1MB to prevent DoS via large files)
    max_size = 1 * 1024 * 1024  # 1MB
    file_size = path.stat().st_size
    if file_size > max_size:
        raise ValueError(f"File too large (max {max_size} bytes): {file_size} bytes")

    # Check file extension (optional but recommended)
    if path.suffix.lower() not in ('.yaml', '.yml'):
        raise ValueError("File must have a .yaml or .yml extension")

    # Read and parse YAML safely
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the entire file first to check for empty content
            content = file.read()
            if not content.strip():
                raise ValueError("File is empty")

            # Use safe_load to prevent arbitrary code execution
            config = yaml.safe_load(content)
            if config is None:  # YAML with only comments returns None
                return {}

            return config

    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML: {str(e)}") from e
    except UnicodeDecodeError as e:
        raise ValueError(f"File is not UTF-8 encoded: {str(e)}") from e
