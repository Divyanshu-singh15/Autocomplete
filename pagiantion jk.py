import requests
import string
import time
import json
import os

base_url = "http://35.200.185.69:8000/v1/autocomplete"
alphabet = string.ascii_lowercase
all_names = set()
request_count = 0

# Load existing names if resuming
if os.path.exists("names_V1.json"):
    with open("names_V1.json", "r") as f:
        all_names.update(json.load(f))
    print(f"Resumed with {len(all_names)} names already collected.")


def fetch_names(prefix):
    """Fetch names for a prefix, handling rate limits."""
    global request_count
    while True:
        response = requests.get(base_url, params={"query": prefix})
        request_count += 1
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited at '{prefix}' after {request_count} requests. Waiting {wait}s...")
            time.sleep(wait)
            continue
        data = response.json()
        return data["results"]


def get_next_query(last_two_names):
    """Determine the next query based on the last two names."""
    if len(last_two_names) < 2:
        return None
    name1, name2 = last_two_names[-2], last_two_names[-1]
    # Find common prefix
    common = ""
    for c1, c2 in zip(name1, name2):
        if c1 == c2:
            common += c1
        else:
            break
    # Next query is common prefix + first divergent char of name2
    if len(common) < len(name2):
        return common + name2[len(common)]
    return None


def extract_names_for_prefix(prefix):
    """Extract all names for a given prefix using pagination."""
    query = prefix
    while True:
        names = fetch_names(query)
        all_names.update(names)
        print(f"Prefix: {prefix}, Query: {query}, Found: {len(names)}, Total: {len(all_names)}")

        if len(names) < 10:  # End of this branch
            break
        if len(names) >= 2:  # Need at least 2 names to paginate
            next_query = get_next_query(names)
            if not next_query or next_query == query:  # No progress possible
                break
            query = next_query
        else:
            break

        # Save progress every 100 requests
        if request_count % 100 == 0:
            with open("names_V1.json", "w") as f:
                json.dump(list(all_names), f)
            print(f"Checkpoint: {len(all_names)} names, {request_count} requests")

        time.sleep(0.2)  # Polite delay to avoid rate limits


# Start with single-letter prefixes
for letter in alphabet:
    extract_names_for_prefix(letter)

# Final save and summary
with open("names_V1.json", "w") as f:
    json.dump(list(all_names), f)

print(f"\nFinal Results:")
print(f"Total unique names: {len(all_names)}")
print(f"Total requests made: {request_count}")
print(f"Names saved to 'names_V1.json'")