import requests
import os

def get_api_data(api_url, api_token):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'User-Agent':'my-app/1.0.0',
        'Accept': 'application/json',
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    api_url = "https://api.example.com/data"
    api_token = os.getenv('API_TOKEN', 'default_token')  # Use environment variable for token
    data = get_api_data(api_url, api_token)
    if data:
        print(data)
