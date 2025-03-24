import requests

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete"

def test_api():
    """Send a test request to analyze the API response format."""
    query = "a"  # Starting with 'a'
    response = requests.get(BASE_URL, params={"query": query})

    if response.status_code == 200:
        print("API Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)

test_api()
