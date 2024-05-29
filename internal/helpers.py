import re

def sanitize_search_query(search_query: str):
    sanitized_query = re.sub(r'[^A-Za-z0-9 ]+', '', search_query)

    return sanitized_query