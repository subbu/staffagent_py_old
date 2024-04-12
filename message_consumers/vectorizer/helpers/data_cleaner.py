import re

def remove_unwanted_chars(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^a-zA-Z0-9@.,+_\- \s]', '', text)
    return text
