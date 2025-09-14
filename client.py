import requests
from typing import Dict, List, Optional, Union, TypedDict, Literal, Any
from datetime import datetime
from dataclasses import dataclass

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Global auth state
auth = ClientAuth()

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

class PollResults(TypedDict):
    poll_id: int
    question: str
    results: List[Dict[str, Any]]

@dataclass
class ClientAuth:
    """Helper class to manage authentication token."""
    token: Optional[str] = None

    def get_headers(self) -> Dict[str, str]:
        """Get headers with authorization if token is available."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

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

def vote_on_poll(poll_id: int, option_id: int) -> Dict[str, Union[bool, str, Dict]]:
    """
    Cast a vote on a specific poll option.
    
    Args:
        poll_id (int): The ID of the poll to vote on
        option_id (int): The ID of the option to vote for
        
    Returns:
        Dict containing:
            - success (bool): Whether the vote was successful
            - data (str or Dict): Success message or error details
    """
    if not auth.token:
        return {
            'success': False,
            'data': 'Authentication required. Please log in first.'
        }
        
    url = f"{BASE_URL}/polls/{poll_id}/vote"
    payload = {"option_id": option_id}
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=auth.get_headers()
        )
        response.raise_for_status()
        
        return {
            'success': True,
            'data': response.json()
        }
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return {
                'success': False,
                'data': 'Unauthorized. Please check your authentication.'
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'data': 'Poll or option not found.'
            }
        return {
            'success': False,
            'data': f'HTTP error occurred: {http_err}'
        }
    except requests.exceptions.RequestException as err:
        return {
            'success': False,
            'data': f'Request error occurred: {err}'
        }

def get_poll_results(poll_id: int) -> Dict[str, Union[bool, str, PollResults]]:
    """
    Retrieve the results for a specific poll.
    
    Args:
        poll_id (int): The ID of the poll to get results for
        
    Returns:
        Dict containing:
            - success (bool): Whether the request was successful
            - data (PollResults or str): Poll results if successful, error message if not
    """
    url = f"{BASE_URL}/polls/{poll_id}/results"
    
    try:
        response = requests.get(url, headers=auth.get_headers())
        response.raise_for_status()
        
        return {
            'success': True,
            'data': response.json()
        }
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return {
                'success': False,
                'data': 'Poll not found.'
            }
        return {
            'success': False,
            'data': f'HTTP error occurred: {http_err}'
        }
    except requests.exceptions.RequestException as err:
        return {
            'success': False,
            'data': f'Request error occurred: {err}'
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
        response = requests.get(url, params=params, headers=auth.get_headers())
        response.raise_for_status()
        
        polls_data = response.json()
        
        return {
            'success': True,
            'data': polls_data,
            'total': int(response.headers.get('x-total-count', len(polls_data))),
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
    # Example registration and authentication
    print("Testing user registration and authentication:")
    result = register_user("testuser", "testpassword123")
    if result["success"]:
        print(f"Registration successful! User ID: {result['data']['id']}")
        # In a real app, you would get the token from the login endpoint
        # For this example, we'll simulate setting the token
        auth.token = "your_jwt_token_here"
    else:
        print(f"Registration failed: {result['data']}")
    
    # Example poll fetching
    print("\nTesting poll fetching:")
    polls_result = get_polls(skip=0, limit=5)
    if polls_result["success"]:
        polls = polls_result["data"]
        print(f"Fetched {len(polls)} polls:")
        for i, poll in enumerate(polls, 1):
            print(f"{i}. {poll['question']} (ID: {poll['id']}, {len(poll['options'])} options)")
            
            # Example: Get results for each poll
            print("   Getting poll results...")
            results = get_poll_results(poll['id'])
            if results["success"]:
                print(f"   Results for '{poll['question']}':")
                for option in results['data']['results']:
                    print(f"   - {option['text']}: {option['vote_count']} votes")
            else:
                print(f"   Failed to get results: {results['data']}")
            
            # Example: Vote on the first option (if there are options)
            if poll['options']:
                option_id = poll['options'][0]['id']
                print(f"   Voting for option ID {option_id}...")
                vote_result = vote_on_poll(poll['id'], option_id)
                if vote_result["success"]:
                    print(f"   Successfully voted! {vote_result['data']}")
                else:
                    print(f"   Failed to vote: {vote_result['data']}")
    else:
        print(f"Failed to fetch polls: {polls_result['data']}")
