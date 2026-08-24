from fastapi import FastAPI
from settings import get_settings
from utils import get_quote_json
from random import randrange
app = FastAPI()


@app.get("/quote")
async def get_random_quote():
    quote_json = get_quote_json(
        quote_path=get_settings().quote_path
    )
    random_quote_index = randrange(len(quote_json["quotes"]))
    random_quote_obj = quote_json["quotes"][random_quote_index]
    return random_quote_obj