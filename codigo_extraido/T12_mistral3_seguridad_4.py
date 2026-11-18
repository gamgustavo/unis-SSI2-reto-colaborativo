import yaml
import os
from typing import Dict, Any
from pathlib import Path

def load_yaml_config(uploaded_file_path: str) -> Dict[str, Any]:
    """
    Safely loads a YAML configuration file into a Python dictionary.

    Args:
        uploaded_file_path: Path to the uploaded YAML file.

    Returns:
        Dictionary containing the YAML configuration.

    Raises:
        ValueError: If the file is empty, too large, or has invalid YAML.
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are insufficient permissions to read the file.
    """
    # Validate file path
    if not uploaded_file_path:
        raise ValueError("File path cannot be empty")

    file_path = Path(uploaded_file_path)

    # Check file existence and permissions
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {uploaded_file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {uploaded_file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Insufficient permissions to read file: {uploaded_file_path}")

    # Check file size (1MB limit to prevent DoS attacks)
    max_file_size = 1 * 1024 * 1024  # 1MB
    file_size = file_path.stat().st_size
    if file_size == 0:
        raise ValueError("File is empty")
    if file_size > max_file_size:
        raise ValueError(f"File too large (max {max_file_size} bytes)")

    # Check file extension
    if file_path.suffix.lower() not in ('.yaml', '.yml'):
        raise ValueError("File must have a .yaml or .yml extension")

    # Safely load YAML content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Use safe_load to prevent arbitrary code execution
            config = yaml.safe_load(file)
            if config is None:  # Handle empty YAML files
                return {}
            return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML content: {str(e)}") from e
    except UnicodeDecodeError as e:
        raise ValueError("File must be UTF-8 encoded") from e
