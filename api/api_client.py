import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

class ApiClient:
    base_url = config["API_URL"]

    
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

    def post(self, endpoint, body=None, params=None):
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, json=body, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None