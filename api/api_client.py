import requests
import os

class ApiClient:
    base_url = os.getenv("API_URL", "http://localhost:8000/api/v1")

    
    def __init__(self):
        self.base_url = ApiClient.base_url

    def get(self, endpoint, params=None):
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

