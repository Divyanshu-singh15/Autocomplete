# File: utils.py

import time
import requests

def rate_limited_request(url, params, retries=3, delay=1):
    """
    Send a GET request with rate limiting and retry logic.
    Adjust delay and retries based on the API behavior.
    """
    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            # If rate limited, wait and retry with exponential backoff
            time.sleep(delay * (2 ** attempt))
        else:
            # For other non-200 status codes, you might want to log or handle them differently
            break
    return response
