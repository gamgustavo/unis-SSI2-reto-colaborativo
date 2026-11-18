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
        ValueError: If the file is not a valid YAML or has unsafe content.
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are insufficient permissions to read the file.
    """
    # Validate the file path
    if not uploaded_file_path:
        raise ValueError("File path cannot be empty.")

    file_path = Path(uploaded_file_path)

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file {uploaded_file_path} does not exist.")

    # Check if the path is a file (not a directory)
    if not file_path.is_file():
        raise ValueError(f"The path {uploaded_file_path} is not a file.")

    # Check file extension to ensure it's a YAML file
    if file_path.suffix.lower() not in ('.yaml', '.yml'):
        raise ValueError("The file must have a .yaml or .yml extension.")

    # Check file size to prevent DoS attacks (e.g., very large files)
    max_file_size = 10 * 1024 * 1024  # 10 MB
    file_size = file_path.stat().st_size
    if file_size > max_file_size:
        raise ValueError(f"File size exceeds the maximum allowed size of {max_file_size} bytes.")

    # Check file permissions (readable by the current user)
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Insufficient permissions to read the file {uploaded_file_path}.")

    # Safely load the YAML file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Use yaml.safe_load to avoid arbitrary code execution
            config = yaml.safe_load(file)
            if config is None:
                return {}
            return config
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML file: {str(e)}")
    except Exception as e:
        raise ValueError(f"An error occurred while reading the file: {str(e)}")
