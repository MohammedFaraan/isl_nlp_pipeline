# utils/helpers.py

def load_list(file_path):
    """Load a list of words from a file."""
    with open(file_path, 'r') as f:
        return [line.strip().lower() for line in f]

def finger_spell(word):
    """Convert a word to its finger-spelled form by separating each letter with a hyphen and converting to uppercase."""
    return " ".join(word.upper())