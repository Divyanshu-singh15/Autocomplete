import time
import requests
import string
from utils import rate_limited_request

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete"


def fetch_results(query):
    """Fetch autocomplete results for a given query."""
    response = rate_limited_request(BASE_URL, params={"query": query})
    if response.status_code == 200:
        data = response.json()
        # Debug: print query and returned count
        print(f"DEBUG: Query '{query}' returned count: {data.get('count', 0)}")
        return data
    else:
        print(f"DEBUG: Query '{query}' failed with status: {response.status_code}")
    return None


def recursive_search(prefix, max_depth=10, results_set=None):
    """Recursively search the API by extending the prefix."""
    if results_set is None:
        results_set = set()

    # Avoid infinite recursion
    if len(prefix) > max_depth:
        return results_set

    data = fetch_results(prefix)
    if not data:
        return results_set

    # Add discovered names to the set
    for name in data.get("results", []):
        results_set.add(name)

    # If count is the max number returned (assuming 10 is max), extend the search.
    if data.get("count", 0) >= 10:
        for char in string.ascii_lowercase:
            recursive_search(prefix + char, max_depth, results_set)

    return results_set


if __name__ == "__main__":
    # Instead of starting with an empty prefix, start with a set of letters.
    all_names = set()
    for letter in string.ascii_lowercase:
        all_names.update(recursive_search(letter))

    print(f"\nTotal names found: {len(all_names)}")
    for name in sorted(all_names):
        print(name)
