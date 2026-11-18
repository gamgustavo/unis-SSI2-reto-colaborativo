import subprocess
import re
import shlex
import sys

def is_valid_hostname(hostname: str) -> bool:
    """Check if the hostname is valid and safe to use in a shell command."""
    if not hostname:
        return False
    # Basic check for valid hostname (simplified, not exhaustive)
    if len(hostname) > 253:
        return False
    # Remove any leading or trailing dots
    hostname = hostname.strip('.')
    # Check each part of the hostname
    if not all(part and len(part) <= 63 and re.match(r'^[a-zA-Z0-9-]+$', part) for part in hostname.split('.')):
        return False
    # Additional check to prevent command injection
    if re.search(r'[;\|\&\$\<\>\(\)\{\}\[\]\~\`\'"\\]', hostname):
        return False
    return True

def ping_host(hostname: str) -> bool:
    """Ping a host and return True if it responds, False otherwise."""
    if not is_valid_hostname(hostname):
        raise ValueError("Invalid or unsafe hostname provided")

    try:
        # Use shlex to properly escape the hostname
        escaped_hostname = shlex.quote(hostname)
        # Determine the appropriate ping command based on the OS
        param = '-n' if sys.platform.lower() == 'win32' else '-c'
        command = ['ping', param, '1', escaped_hostname]

        # Run the ping command with a timeout
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False
        )

        # Check if the ping was successful
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Ping to {hostname} timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"An error occurred while pinging {hostname}: {str(e)}", file=sys.stderr)
        return False

def main():
    """Main function to get user input and ping the host."""
    try:
        hostname = input("Enter the hostname or IP address to ping: ").strip()
        if ping_host(hostname):
            print(f"{hostname} is responding to ping.")
        else:
            print(f"{hostname} is not responding to ping.")
    except ValueError as ve:
        print(f"Error: {str(ve)}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    main()
