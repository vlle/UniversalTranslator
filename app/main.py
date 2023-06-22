from contextlib import asynccontextmanager
from typing import Union

from fastapi import FastAPI

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    pass


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# register animal
# translate animal to human
# translate animal to another animal
# translate human to animal
