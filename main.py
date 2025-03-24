import requests
import string
alphabet = string.ascii_lowercase

base_url = "http://35.200.185.69:8000/v2/autocomplete"

q='a'
response = requests.get(base_url, params={"query": q})
print(f"Query: {q}")
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

import requests
from collections import deque


def common_prefix_plus_one(word1, word2):
    """
    Compute the common prefix between word1 and word2.
    Then append one extra letter from word2 (if available) right after the common prefix.
    """
    cp = ""
    # Find common prefix between the two words.
    for a, b in zip(word1, word2):
        if a == b:
            cp += a
        else:
            break
    # Append one more letter from word2 if possible.
    if len(word2) > len(cp):
        cp += word2[len(cp)]
    return cp


def lexicographical_search_bfs_api_common():
    # Base API URL for autocomplete requests.
    base_url = "http://35.200.185.69:8000/v2/autocomplete"

    # Characters in lexicographical order (digits first, then letters).
    chars = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
        "u", "v", "w", "x", "y", "z"
    ]

    # Maximum allowed depth (word length).
    max_depth = 1

    # Dictionary to store the computed API info for each node.
    # Key: current string (node), Value: computed string (common prefix plus one extra letter)
    api_info = {}

    # Initialize the queue with an empty string node.
    queue = deque([""])

    while queue:
        current_string = queue.popleft()

        # For non-empty strings, perform the API request.
        if current_string:
            response = requests.get(base_url, params={"query": current_string})
            print(f"Query: {current_string}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}\n")

            # Parse JSON response and extract the results.
            data = response.json()
            results = data.get("results", [])

            # If we have at least two words in the results, compute the common prefix plus one letter.
            if len(results) >= 2:
                computed = common_prefix_plus_one(results[-2], results[-1])
            else:
                computed = ""
            api_info[current_string] = computed
        else:
            # For the empty string, just store an empty string.
            api_info[current_string] = ""

        # Do not extend the node further if it reached the maximum allowed length.
        if len(current_string) >= max_depth:
            continue

        # Enqueue new nodes by appending each character.
        for char in chars:
            queue.append(current_string + char)

    # Print the stored API info for each node.
    print("Stored API info for nodes (computed common prefix + one extra letter):")
    for node, value in api_info.items():
        print(f"Node: '{node}' => {value}")


if __name__ == "__main__":
    lexicographical_search_bfs_api_common()
