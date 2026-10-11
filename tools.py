import json

def write(subject: str, description: str, filename: str = "memory.json") -> str:
    """Saves a key-value fact to the persistent JSON memory file."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[subject] = description

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return f"Successfully saved memory for '{subject}'."


def read(filename: str = "memory.json") -> dict:
    """Reads all key-value facts from the persistent JSON memory file."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    return data