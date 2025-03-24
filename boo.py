import requests
import string
import time
import json
import os

base_url = "http://35.200.185.69:8000/v1/autocomplete"
alphabet = string.ascii_lowercase
all_names = set()
excluded_prefixes = set()
request_count = 0

# Load existing data if resuming
if os.path.exists("names_V1.json"):
    with open("names_V1.json", "r") as f:
        all_names.update(json.load(f))
    print(f"Resumed with {len(all_names)} names.")
if os.path.exists("excluded_V1.json"):
    with open("excluded_V1.json", "r") as f:
        excluded_prefixes.update(json.load(f))
    print(f"Loaded {len(excluded_prefixes)} excluded prefixes.")


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


def get_excluded_prefixes(prefix, names):
    """Exclude prefixes using the three-word rule (if 10) or low count (if <10)."""
    exclusions = set()

    # Rule 1: If <10 results, exclude all deeper prefixes
    if len(names) < 10 and len(names) > 0:
        exclusions.add(prefix)

    # Rule 2: If 10 results, use first and last two words
    elif len(names) == 10 and len(names) >= 3:
        first_name = names[0]
        second_last = names[-2]
        last_name = names[-1]

        # Exclude from just after first_name up to second_last's prefix
        if len(first_name) >= len(prefix) and len(second_last) > len(prefix):
            base = prefix
            start_char = first_name[len(prefix)] if len(first_name) > len(prefix) else 'a'
            end_char = second_last[len(prefix)]
            for c in alphabet:
                if start_char <= c <= end_char:
                    exclusions.add(base + c)
            # If second_last is longer, exclude up to its full prefix
            if len(second_last) > len(prefix) + 1:
                exclusions.add(second_last[:len(prefix) + 1])

    return exclusions


def get_next_prefix(names):
    """Determine the next prefix from the last two names when 10 results are returned."""
    if len(names) < 10 or len(names) < 2:
        return None
    second_last, last = names[-2], names[-1]
    common = ""
    for c1, c2 in zip(second_last, last):
        if c1 == c2:
            common += c1
        else:
            break
    if len(common) < len(last):
        return common + last[len(common)]
    return None


def explore_prefix(prefix, max_depth=4):
    """Explore prefixes with the three-word exclusion rule."""
    if prefix in excluded_prefixes or len(prefix) > max_depth:
        return

    # Skip if this prefix extends an excluded base
    for excluded in excluded_prefixes:
        if prefix.startswith(excluded) and len(prefix) > len(excluded):
            return

    names = fetch_names(prefix)
    all_names.update(names)
    print(f"Prefix: {prefix}, Found: {len(names)}, Total: {len(all_names)}")

    # Update exclusions
    new_exclusions = get_excluded_prefixes(prefix, names)
    excluded_prefixes.update(new_exclusions)

    # If 10 results, jump to the next prefix from the last two names
    if len(names) == 10:
        next_prefix = get_next_prefix(names)
        if next_prefix and next_prefix not in excluded_prefixes:
            explore_prefix(next_prefix, max_depth)

    # Explore deeper, skipping exclusions
    if len(names) > 0:
        for letter in alphabet:
            deeper_prefix = prefix + letter
            skip = deeper_prefix in excluded_prefixes
            for excluded in excluded_prefixes:
                if deeper_prefix.startswith(excluded):
                    skip = True
                    break
            if not skip:
                explore_prefix(deeper_prefix, max_depth)

    # Save progress every 100 requests
    if request_count % 100 == 0:
        with open("names_V1.json", "w") as f:
            json.dump(list(all_names), f)
        with open("excluded_V1.json", "w") as f:
            json.dump(list(excluded_prefixes), f)
        print(f"Checkpoint: {len(all_names)} names, {len(excluded_prefixes)} excluded, {request_count} requests")


# Start with single-letter prefixes
for letter in alphabet:
    explore_prefix(letter, max_depth=4)

# Final save and summary
with open("names_V1.json", "w") as f:
    json.dump(list(all_names), f)
with open("excluded_V1.json", "w") as f:
    json.dump(list(excluded_prefixes), f)

print(f"\nFinal Results:")
print(f"Total unique names: {len(all_names)}")
print(f"Total requests made: {request_count}")
print(f"Excluded prefixes: {len(excluded_prefixes)}")
print(f"Data saved to 'names_V1.json' and 'excluded_V1.json'")