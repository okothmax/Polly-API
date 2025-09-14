import requests
from typing import Dict, List, Optional, Union, TypedDict, Literal
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Type definitions for better type hinting
class OptionOut(TypedDict):
    id: int
    text: str
    poll_id: int

class PollOut(TypedDict):
    id: int
    question: str
    created_at: str  # ISO format datetime
    owner_id: int
    options: List[OptionOut]

class PollsResponse(TypedDict):
    success: bool
    data: Union[List[PollOut], str]
    total: Optional[int]
    skip: int
    limit: int

def register_user(username: str, password: str) -> Dict[str, Union[bool, Dict, str]]:
    """
    Register a new user with the given username and password.
    
    Args:
        username (str): The username for the new user
        password (str): The password for the new user
        
    Returns:
        Dict containing:
            - success (bool): Whether the registration was successful
            - data (Dict or str): The response data if successful, error message if not
    """
    url = f"{BASE_URL}/register"
    payload = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        return {
            "success": True,
            "data": response.json()
        }
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 400:
            return {
                "success": False,
                "data": "Username already registered"
            }
        return {
            "success": False,
            "data": f"HTTP error occurred: {http_err}"
        }
    except requests.exceptions.RequestException as err:
        return {
            "success": False,
            "data": f"Request error occurred: {err}"
        }

def get_polls(skip: int = 0, limit: int = 10) -> PollsResponse:
    """
    Fetches paginated poll data from the API.
    
    Args:
        skip (int): Number of items to skip (for pagination)
        limit (int): Maximum number of items to return (for pagination)
        
    Returns:
        Dict containing:
            - success (bool): Whether the request was successful
            - data (List[PollOut] or str): List of polls if successful, error message if not
            - total (int, optional): Total number of polls available (if provided by API)
            - skip (int): The skip value used in the request
            - limit (int): The limit value used in the request
    """
    url = f"{BASE_URL}/polls"
    params = {
        'skip': max(0, skip),
        'limit': max(1, min(100, limit))  # Enforce reasonable limits
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        polls_data = response.json()
        
        return {
            'success': True,
            'data': polls_data,
            'total': int(response.headers.get('x-total-count', 0)),
            'skip': params['skip'],
            'limit': params['limit']
        }
        
    except requests.exceptions.HTTPError as http_err:
        return {
            'success': False,
            'data': f"HTTP error occurred: {http_err}",
            'total': 0,
            'skip': params['skip'],
            'limit': params['limit']
        }
    except requests.exceptions.RequestException as err:
        return {
            'success': False,
            'data': f"Request error occurred: {err}",
            'total': 0,
            'skip': params['skip'],
            'limit': params['limit']
        }

# Example usage
if __name__ == "__main__":
    # Example registration
    print("Testing user registration:")
    result = register_user("testuser", "testpassword123")
    if result["success"]:
        print(f"Registration successful! User ID: {result['data']['id']}")
    else:
        print(f"Registration failed: {result['data']}")
    
    # Example poll fetching
    print("\nTesting poll fetching:")
    polls_result = get_polls(skip=0, limit=5)
    if polls_result["success"]:
        polls = polls_result["data"]
        print(f"Fetched {len(polls)} polls:")
        for i, poll in enumerate(polls, 1):
            print(f"{i}. {poll['question']} ({len(poll['options'])} options)")
    else:
        print(f"Failed to fetch polls: {polls_result['data']}")
