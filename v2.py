import requests
import time
import json
from collections import deque


def common_prefix_plus_one(word1, word2):
    """
    Compute the common prefix between word1 and word2.
    Then append one extra letter from word2 (if available) right after the common prefix.
    """
    cp = ""
    for a, b in zip(word1, word2):
        if a == b:
            cp += a
        else:
            break
    if len(word2) > len(cp):
        cp += word2[len(cp)]
    return cp


def save_names_to_file(names_store, filename="namesv1.json"):
    """
    Save the collected names to a JSON file under key "namev2".
    """
    with open(filename, "w") as f:
        json.dump({"namev2": names_store}, f, indent=4)
    print(f"Saved {len(names_store)} nodes to {filename}")


def lexicographical_search_bfs_api_common_skip_none_save():
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
    max_depth = 4

    # Dictionary to store computed API info for each node (computed common prefix plus one extra letter or "NONE").
    api_info = {}
    # Dictionary to store the names (API response "results") for each node.
    names_store = {}

    # Counters for logging and saving.
    total_requests = 0
    total_names = 0

    # Initialize the queue with an empty string node.
    queue = deque([""])

    while queue:
        current_string = queue.popleft()

        # Process non-empty nodes by making an API request.
        if current_string:
            while (True):
                response = requests.get(base_url, params={"query": current_string})
                if response.status_code != 200:
                    print("Error in response. Retrying...", response.status_code, response.text)
                    time.sleep(2)
                    continue
                else:
                    break
            total_requests += 1
            data = response.json()
            results = data.get("results", [])

            # Log the clean output.
            total_names += len(results)
            log_line = (f"Query: {current_string} | Words Found: {len(results)} | "
                        f"Total Names: {total_names} | Total Requests: {total_requests}")
            print(log_line)

            # Save the results for this node.
            names_store[current_string] = results

            # Save to file after every 50 requests.
            if total_requests % 50 == 0:
                save_names_to_file(names_store)

            # If the response contains fewer than 12 words, store "NONE" and skip exploring its children.
            if len(results) < 12:
                api_info[current_string] = "NONE"
                # Wait before next request.
                time.sleep(1.25)
                continue
            else:
                # If there are at least two words, compute common prefix plus one extra letter.
                if len(results) >= 2:
                    computed = common_prefix_plus_one(results[-2], results[-1])
                else:
                    computed = ""
                api_info[current_string] = computed

            # Wait to respect the API rate limit.
            time.sleep(1.25)
        else:
            # For the empty node, store an empty string.
            api_info[current_string] = ""

        # If maximum depth reached, don't generate children.
        if len(current_string) >= max_depth:
            continue

        # Retrieve the parent's stored computed value.
        parent_stored = api_info.get(current_string, "")

        # If parent's stored value is "NONE", skip generating children.
        if parent_stored == "NONE":
            continue

        # Generate child nodes by appending each character.
        for char in chars:
            child = current_string + char
            # If parent's stored word exists and child is lexicographically less than it, skip enqueuing this child.
            if parent_stored and child < parent_stored:
                continue
            queue.append(child)

    # Final save once all nodes are processed.
    save_names_to_file(names_store)
    print("Final stored API info (computed values):")
    for node, value in api_info.items():
        print(f"Node: '{node}' => {value}")


if __name__ == "__main__":
    lexicographical_search_bfs_api_common_skip_none_save()
