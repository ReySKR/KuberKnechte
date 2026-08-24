import os
import requests
from functools import lru_cache

@lru_cache
def _get_quote_endpoint() -> str:
    if not os.getenv("IS_PROD"):
        from dotenv import load_dotenv
        load_dotenv()

    if not os.getenv("QUOTE_ENDPOINT_URL"):
        raise ValueError("'QUOTE_ENDPOINT_URL' not set.")
    
    return os.getenv("QUOTE_ENDPOINT_URL")

def get_quote() -> dict[str, str]:
    quote_dict = requests.get(url=_get_quote_endpoint())
    return quote_dict.json()