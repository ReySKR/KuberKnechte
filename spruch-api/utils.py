import json
from functools import lru_cache

@lru_cache
def get_quote_json(quote_path: str) -> dict[str, list[dict[str, str]]]:
    try:
        with open(quote_path) as f:
            quote_dict: dict[str, list[dict[str, str]]] = json.load(f)
    except:
        raise ValueError("Quote path not found.")

    if not "quotes" in quote_dict:
        raise KeyError("List of quotes not found. Identified by key 'quotes'.")

    if not "quote" in quote_dict["quotes"][0] and not "category" in quote_dict["quotes"][0]:
        raise KeyError("Key 'quote' or 'category' not found in quote json")

    return quote_dict
    