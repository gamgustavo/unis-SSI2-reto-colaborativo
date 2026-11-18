import os
import zipfile
import tempfile
from pathlib import Path
import shutil
import re

def sanitize_filename(filename: str) -> str:
    """Sanitize the filename to prevent directory traversal and other attacks."""
    # Remove null bytes
    filename = filename.replace('\x00', '')
    # Normalize path to prevent directory traversal
    filename = os.path.normpath(filename)
    # Prevent absolute paths
    if os.path.isabs(filename):
        filename = os.path.basename(filename)
    # Remove any remaining path traversal attempts
    filename = re.sub(r'[\\/]+', '_', filename)
    return filename

def extract_zip_file(uploaded_zip_file, extract_to: str = 'descargas') -> bool:
    """
    Safely extract a ZIP file uploaded by the user to the specified directory.

    Args:
        uploaded_zip_file: A file-like object representing the uploaded ZIP file.
        extract_to: The directory where the contents will be extracted (default: 'descargas').

    Returns:
        bool: True if extraction was successful, False otherwise.

    Raises:
        ValueError: If the uploaded file is not a valid ZIP file or if there are security issues.
    """
    # Validate the target directory
    extract_to = os.path.abspath(extract_to)
    if not os.path.exists(extract_to):
        os.makedirs(extract_to, exist_ok=True)
    elif not os.path.isdir(extract_to):
        raise ValueError("The extraction path exists and is not a directory.")

    # Create a temporary file to safely handle the uploaded ZIP
    with tempfile.NamedTemporaryFile(delete=False) as temp_zip:
        try:
            # Write the uploaded file to a temporary location
            shutil.copyfileobj(uploaded_zip_file, temp_zip)
            temp_zip_path = temp_zip.name
        except Exception as e:
            raise ValueError(f"Failed to write the uploaded file to a temporary location: {e}")

    try:
        # Verify the file is a valid ZIP
        if not zipfile.is_zipfile(temp_zip_path):
            raise ValueError("The uploaded file is not a valid ZIP file.")

        # Open the ZIP file and extract its contents safely
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            # Check for zip bombs (e.g., extremely large files or too many files)
            total_uncompressed_size = sum(file.file_size for file in zip_ref.infolist())
            max_size = 100 * 1024 * 1024  # 100 MB limit for uncompressed size
            if total_uncompressed_size > max_size:
                raise ValueError("The ZIP file is too large to extract safely.")

            # Extract each file safely
            for file in zip_ref.infolist():
                # Sanitize the filename to prevent directory traversal
                sanitized_filename = sanitize_filename(file.filename)
                if not sanitized_filename:
                    continue  # Skip empty filenames

                # Construct the full path where the file will be extracted
                target_path = os.path.join(extract_to, sanitized_filename)

                # Ensure the target path is within the extraction directory
                if not os.path.abspath(target_path).startswith(extract_to):
                    raise ValueError(f"Attempted directory traversal detected: {file.filename}")

                # Create directories if necessary
                if file.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    # Ensure the parent directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    # Extract the file
                    with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)

    except zipfile.BadZipFile:
        raise ValueError("The uploaded file is not a valid ZIP file or is corrupted.")
    except Exception as e:
        raise ValueError(f"An error occurred while extracting the ZIP file: {e}")
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_zip_path)
        except Exception:
            pass

    return True
