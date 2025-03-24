import requests


def lexicographical_search(base_url):
    # Characters in lexicographical order (digits first, then letters)
    chars = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
        "u", "v", "w", "x", "y", "z"
    ]

    # Set to keep track of explored prefixes
    explored_prefixes = set()

    # Helper function to get the next prefix in lexicographical order
    def get_next_prefix(current):
        if not current:
            return chars[0]  # Start with the first character

        # Try to increment the last character
        last_char = current[-1]
        try:
            last_char_index = chars.index(last_char)
            # If we can increment the last character
            if last_char_index < len(chars) - 1:
                return current[:-1] + chars[last_char_index + 1]
            else:
                # If we can't increment the last character, move to the next level
                if len(current) == 1:
                    # If at the top level, move to the next character
                    first_char_index = chars.index(current[0])
                    if first_char_index < len(chars) - 1:
                        return chars[first_char_index + 1]
                    else:
                        return None  # We've completed the search
                else:
                    # Get the next prefix at the higher level and add the first character
                    higher_level_next = get_next_prefix(current[:-1])
                    if higher_level_next:
                        return higher_level_next + chars[0]
                    else:
                        return None  # We've completed the search
        except ValueError:
            # If character not found, just return None
            return None

    def explore(prefix=""):
        if prefix in explored_prefixes:
            return

        explored_prefixes.add(prefix)

        # Make request to server with current prefix
        response = requests.get(base_url, params={"query": prefix})
        print(f"Query: {prefix if prefix else 'empty'}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}\n")

        # Parse response
        response_data = response.json()
        results = response_data.get("results", [])
        count = response_data.get("count", 0)

        # If we got exactly 12 results, use the optimization to jump ahead
        if count == 12:
            last_two = results[-2:]
            if len(last_two) >= 2:
                word1, word2 = last_two

                # Find first differing position
                min_len = min(len(word1), len(word2))
                first_diff_pos = None

                for i in range(min_len):
                    if word1[i] != word2[i]:
                        first_diff_pos = i
                        break

                if first_diff_pos is not None:
                    # The next query should be the prefix up to and including the first differing character
                    next_query = word2[:first_diff_pos + 1]
                    explore(next_query)
                else:
                    # If no difference found in common prefix, take the longer word's next character
                    if len(word2) > min_len:
                        next_query = word2[:min_len + 1]
                        explore(next_query)

        # If count < 12 or we've explored the branch optimized from last elements,
        # move to the next prefix in lexicographical order
        next_prefix = get_next_prefix(prefix)
        if next_prefix:
            explore(next_prefix)

    # Start the exploration
    explore("")

# Example usage:
lexicographical_search("http://35.200.185.69:8000/v2/autocomplete")